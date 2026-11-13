import { addItem } from "./cart";
test("adding an item keeps earlier items", () => {
  expect(addItem(["a"], "b")).toEqual(["a", "b"]);
});
