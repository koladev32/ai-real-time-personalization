import random
import sqlite3
from datetime import datetime

from vowpalwabbit import pyvw

class RecommendationEngine:
    def __init__(self, db_path="./db/ecommerce.db"):
        self.db_path = db_path
        self.vw = pyvw.Workspace("--cb_explore_adf --epsilon 0.2 -q UA --quiet")

    # Database Utilities
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def query_db(self, query, args=(), one=False):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(query, args)
        result = cur.fetchall()
        conn.close()
        return (result[0] if result else None) if one else result

    # Event Processing
    def process_event_batch(self, events):
        """
        Processes a batch of events to compute recommendation scores.
        """
        score_data = {}
        total_weight = 0
        weight = 1.0
        weight_decay = 0.9

        for event in reversed(events):
            context = self.get_context(event)
            actions = self.get_possible_actions(event)
            reward = self.get_reward(event["event_type"])

            for action, prob in zip(actions, self.vw.predict(self.format_vw_example(context, actions))):
                score_data[action] = score_data.get(action, 0) + (reward * prob * weight)

            total_weight += weight
            weight *= weight_decay

        score_data = {k: v / total_weight for k, v in score_data.items()}
        recommendations = sorted(score_data, key=score_data.get, reverse=True)

        return score_data, recommendations[:10]

    # Context and Action Retrieval
    def get_context(self, event):
        """
        Extracts context features from the event.
        """
        return {
            "session_id": event["session_id"],
            "time_of_day": datetime.strptime(event.get("timestamp").replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f").hour,
            "device": event.get("additional_context", {}).get("device_type", "unknown"),
        }

    def get_possible_actions(self, event, limit=10):
        """
        Fetches product IDs as possible actions, balancing recency and popularity.
        """
        category_id = self.get_event_category_id(event)
        category_products = self.query_db(
            """
            SELECT p.id FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE c.id = ?
            LIMIT ?
            """,
            (category_id, int(limit / 2))
        )

        popular_products = self.query_db(
            "SELECT id FROM products ORDER BY rating DESC LIMIT ?",
            (limit - len(category_products),)
        )

        all_products = [product["id"] for product in category_products] + \
                       [product["id"] for product in popular_products]
        random.shuffle(all_products)

        return all_products[:limit]

    def get_event_category_id(self, event):
        """
        Determines the category ID based on event type.
        """
        return event["category_id"] if event["event_type"] == "click_category" else \
            self.query_db("SELECT category_id FROM products WHERE id = ?", (event["product_id"],), one=True)["category_id"]

    # Vowpal Wabbit Integration
    def get_action(self, context, actions):
        vw_format = self.format_vw_example(context, actions)
        pmf = self.vw.predict(vw_format)
        chosen_action_index, prob = self.sample_pmf(pmf)
        return actions[chosen_action_index], prob

    def format_vw_example(self, context, actions, chosen_action=None, reward=None, prob=None):
        """
        Formats the Vowpal Wabbit input example with context and actions.
        """
        example = f"shared |User session_id={context['session_id']} time_of_day={context['time_of_day']} device={context['device']}\n"
        for action in actions:
            if chosen_action and action == chosen_action:
                example += f"0:{reward}:{prob} |Action product={action}\n"
            else:
                example += f"|Action product={action}\n"
        return example.strip()

    # Utility Functions
    def sample_pmf(self, pmf):
        """
        Samples from a probability mass function (PMF).
        """
        total = sum(pmf)
        normalized_pmf = [p / total for p in pmf]
        cumulative = 0.0
        rand = random.random()
        for i, prob in enumerate(normalized_pmf):
            cumulative += prob
            if cumulative > rand:
                return i, prob
        return len(pmf) - 1, normalized_pmf[-1]

    def get_reward(self, event_type):
        """
        Maps event types to reward values for Vowpal Wabbit.
        """
        rewards = {
            "view_product": 0.1,
            "click_category": 0.2,
            "add_to_cart": 0.3,
            "purchase": 0.5,
            "rate_product_positive": 0.6,
            "rate_product_negative": 0.1,
            "search": 0.1,
            "add_to_wishlist": 0.1,
            "remove_from_wishlist": 0.1,
            "view_wishlist": 0.1,
            "share": 0.1,
            "view_cart": 0.1,
        }
        return rewards.get(event_type, 0)
