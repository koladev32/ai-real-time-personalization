// components/Sidebar.js
"use client";
import { useEffect, useState } from "react";
import { fetchFromAPI } from "../utils/api";
import { trackEvent } from "@/utils/tracking";

export default function Sidebar({ onCategorySelect }) {
  const [categories, setCategories] = useState([]);

  const handleClick = (categoryId) => {
    trackEvent("click_category", { category_id: categoryId });
  };

  useEffect(() => {
    async function fetchCategories() {
      try {
        const data = await fetchFromAPI("/categories");
        setCategories(data);
      } catch (error) {
        console.error("Failed to fetch categories:", error);
      }
    }
    fetchCategories();
  }, []);

  return (
    <aside className="w-64 bg-white text-gray-900 p-4">
      <h2 className="text-xl font-bold mb-4">Collections</h2>
      <ul>
        {categories.map((category) => (
          <li
            key={category.id}
            className="mb-2 cursor-pointer hover:text-blue-400"
            onClick={() => {
              onCategorySelect(category.id);
              handleClick(category.id);
            }}
          >
            {category.category_name}
          </li>
        ))}
      </ul>
    </aside>
  );
}
