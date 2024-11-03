import random
import sqlite3
from datetime import datetime

from vowpalwabbit import pyvw

from utils.redis_client import get_redis_connection

# Utility function to execute queries
def query_db(query, args=(), one=False):
    conn = sqlite3.connect("./db/ecommerce.db")
    conn.row_factory = sqlite3.Row  # Enables column access by name
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Initialize Vowpal Wabbit with Contextual Bandit
vw = pyvw.Workspace("--cb_explore_adf --epsilon 0.2 -q UA --quiet")


def process_event_batch(events):
    """
    Processes a batch of events, computing recommendation scores based on recent interactions.
    """
    # Initialize empty score data
    score_data = {}

    for event in events:
        context = get_context(event)
        actions = get_possible_actions(event)
        reward = get_reward(event["event_type"])

        # Update score for each action
        for action, prob in zip(actions, vw.predict(format_vw_example(context, actions))):
            score_data[action] = score_data.get(action, 0) + (reward * prob)

    # Normalize scores to get a ranking of recommendations
    total_score = sum(score_data.values())
    score_data = {k: v / total_score for k, v in score_data.items()}  # Normalize
    recommendations = sorted(score_data, key=score_data.get, reverse=True)

    return score_data, recommendations[:5]  # Return top 5 recommendations


def get_context(event):
    return {
        "session_id": event["session_id"],
        "time_of_day": datetime.strptime(event.get('timestamp').replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f").hour,
        "device": event.get("additional_context", {}).get("device_type", "unknown")
    }


def get_possible_actions(event, limit=10):
    """
    Fetch product IDs as possible actions for a given category.
    Uses the category_slug to get relevant product recommendations.
    """

    if event["event_type"] == "click_category":
        category_id = event["category_id"]
    else:
        product = query_db("SELECT category_id FROM products WHERE id = ?", (event["product_id"],), one=True)
        category_id = product["category_id"]

    query = """
    SELECT p.id FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE c.id = ?
    LIMIT ?
    """
    # Retrieve product IDs that belong to the specified category
    products = query_db(query, (category_id, limit))

    # Return just the product IDs
    return [product["id"] for product in products]


def get_action(workspace, context, actions):
    vw_format = format_vw_example(context, actions)
    pmf = workspace.predict(vw_format)

    chosen_action_index, prob = sample_pmf(pmf)
    return actions[chosen_action_index], prob


def format_vw_example(context, actions, chosen_action=None, reward=None, prob=None):
    example = f"shared |User session_id={context['session_id']} time_of_day={context['time_of_day']} device={context['device']}\n"
    for action in actions:
        if chosen_action and action == chosen_action:
            example += f"0:{reward}:{prob} |Action product={action}\n"
        else:
            example += f"|Action product={action}\n"
    return example.strip()


def sample_pmf(pmf):
    total = sum(pmf)
    pmf = [p / total for p in pmf]
    cumulative = 0.0
    rand = random.random()
    for i, prob in enumerate(pmf):
        cumulative += prob
        if cumulative > rand:
            return i, prob
    return len(pmf) - 1, pmf[-1]


def get_reward(event_type):
    rewards = {
        "view_product": 0.2,
        "click_category": 0.5,
        "add_to_cart": 0.8,
        "purchase": 1.0
    }
    return rewards.get(event_type, 0)