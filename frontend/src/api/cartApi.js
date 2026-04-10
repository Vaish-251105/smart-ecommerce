import api from "./axios";

export const addToCart = (data) => {
  return api.post("cart/", data);
};

export const getCart = () => {
  return api.get("cart/");
};