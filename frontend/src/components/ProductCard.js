// components/ProductCard.js
"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";

export default function ProductCard({ product }) {
  const router = useRouter();

  // Truncate title to the first three words if it's longer than three words
  const truncatedTitle = product.title.split(" ").length > 3
    ? product.title.split(" ").slice(0, 3).join(" ") + "..."
    : product.title;

  return (
    <div
      className="bg-white text-gray-900 rounded-lg shadow-lg p-4 hover:border-blue-500 hover:border-2 hover:cursor-pointer"
      onClick={() => {
        router.push(`/products/${product.id}`);
      }}
    >
      <div className="w-full h-48 relative mb-4 rounded-lg overflow-hidden">
        <Image
          src={
            product.imgUrl ||
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
      <h3 className="text-lg font-semibold">{truncatedTitle}</h3>
      <p className="text-blue-400 text-xl">${product.price}</p>
      <p className="text-gray-400 mt-1">Rating: {product.stars}</p>
    </div>
  );
}