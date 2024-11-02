"use client";
import { useState, useEffect } from "react";
import ProductCard from "../components/ProductCard";
import SearchBar from "../components/SearchBar";
import SortMenu from "../components/SortMenu";
import Pagination from "../components/Pagination";

const mockProducts = Array.from({ length: 100 }, (_, i) => ({
  id: i + 1,
  name: `Product ${i + 1}`,
  price: (Math.random() * 100).toFixed(2),
  image: "https://via.placeholder.com/150",
}));

export default function Home() {
  const [products, setProducts] = useState(mockProducts);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("Relevance");
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 12;

  useEffect(() => {
    const filteredProducts = mockProducts.filter((product) =>
      product.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (sortOption === "Price: Low to high") {
      filteredProducts.sort((a, b) => a.price - b.price);
    } else if (sortOption === "Price: High to low") {
      filteredProducts.sort((a, b) => b.price - a.price);
    }

    const indexOfLastProduct = currentPage * productsPerPage;
    const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
    const currentProducts = filteredProducts.slice(
      indexOfFirstProduct,
      indexOfLastProduct
    );

    setProducts(currentProducts);
  }, [searchTerm, sortOption, currentPage]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <SearchBar onSearch={setSearchTerm} />
        <SortMenu onSort={setSortOption} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      <Pagination
        currentPage={currentPage}
        totalPages={Math.ceil(mockProducts.length / productsPerPage)}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}
