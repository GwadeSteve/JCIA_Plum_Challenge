import React from "react";
import { FiZap } from "react-icons/fi";
import "./PredictButton.css";

const PredictButton = ({ onClick, isLoading }) => {
  return (
    <button
      className={`predict-button ${isLoading ? "loading" : ""}`}
      onClick={onClick}
      disabled={isLoading}
    >
      {isLoading ? (
        <div className="loading-spinner"></div>
      ) : (
        <>
          <FiZap size={20} />
          <span>Predict</span>
        </>
      )}
    </button>
  );
};

export default PredictButton;
