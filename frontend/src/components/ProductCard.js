// components/ProductCard.js
"use client";

import Image from "next/image";

export default function ProductCard({ product }) {
  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-4">
      <div className="w-full h-48 relative mb-4 rounded-lg overflow-hidden">
        <Image
          src={product.image}
          alt={product.name}
          layout="fill" // Fill the container
          objectFit="cover" // Crop to fill the container if needed
          placeholder="blur" // Optional: use placeholder blur effect
          blurDataURL="https://via.placeholder.com/150" // Optional: provide a placeholder
        />
      </div>
      <h3 className="text-lg font-semibold">{product.name}</h3>
      <p className="text-blue-400 text-xl">${product.price}</p>
    </div>
  );
}
