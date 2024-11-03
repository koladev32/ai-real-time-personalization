// components/ProductCard.js
"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";

export default function ProductCard({ product }) {
  const router = useRouter();
  return (
    <div
      className="bg-gray-800 rounded-lg shadow-lg p-4 hover:border-blue-500 hover:border-2 hover:cursor-pointer"
      onClick={() => {
        router.push(`/products/${product.id}`);
      }}
    >
      <div className="w-full h-48 relative mb-4 rounded-lg overflow-hidden">
        <Image
          src={
            product.thumbnail ||
            `https://dummyjson.com/image/400x200/FF0000/FFFFFF?text=${product.title.replace(
              " ",
              "+"
            )}`
          }
          alt={product.title}
          layout="fill"
          objectFit="cover"
        />
      </div>
      <h3 className="text-lg font-semibold">{product.title}</h3>
      <p className="text-blue-400 text-xl">${product.price}</p>
      <p className="text-gray-400 mt-1">Rating: {product.rating}</p>
    </div>
  );
}
