"use client";

const categories = [
  "All",
  "Bags",
  "Drinkware",
  "Electronics",
  "Footwear",
  "Headwear",
  "Hoodies",
  "Jackets",
  "Kids",
  "Pets",
  "Shirts",
  "Stickers",
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-800 p-4">
      <h2 className="text-xl font-bold mb-4">Collections</h2>
      <ul>
        {categories.map((category) => (
          <li
            key={category}
            className="mb-2 cursor-pointer hover:text-blue-400"
          >
            {category}
          </li>
        ))}
      </ul>
    </aside>
  );
}
