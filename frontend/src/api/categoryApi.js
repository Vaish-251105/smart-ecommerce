import api from "./axios";

export const getCategories = () => {
  return api.get("categories/");
};
