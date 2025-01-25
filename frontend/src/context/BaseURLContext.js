import { createContext } from "react";

const BASE_URL = "http://localhost:5001";
const BaseURLContext = createContext(BASE_URL);

export { BaseURLContext };
