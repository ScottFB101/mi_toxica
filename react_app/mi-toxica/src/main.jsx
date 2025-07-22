import React from "react";
import { createRoot } from "react-dom/client";
import SpanishTeacherChat from "./App.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <SpanishTeacherChat />
  </React.StrictMode>
);
