import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";

import * as itemsApi from "./api/itemsApi";

jest.mock("./api/itemsApi");

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe("React + Django CRUD UI", () => {
  test("renders and loads items on mount", async () => {
    const listMock = jest.spyOn(itemsApi, "listItemsCursor");
    listMock.mockResolvedValue({
      next: null,
      previous: null,
      results: [{ id: 1, title: "hello", description: "desc", created_at: "t", updated_at: "u" }],
    });

    renderWithQuery(<App />);

    // App uses debounce (250ms) before first load.
    await waitFor(() => {
      expect(screen.getByText("hello")).toBeInTheDocument();
    });
  });

  test("Create triggers POST and reloads list", async () => {
    const user = userEvent.setup({ delay: null });

    jest.spyOn(itemsApi, "createItem").mockResolvedValue({
      id: 2,
      title: "new",
      description: "d",
      created_at: "t",
      updated_at: "u",
    });

    const listMock = jest.spyOn(itemsApi, "listItemsCursor");
    listMock
      .mockResolvedValueOnce({
        next: null,
        previous: null,
        results: [{ id: 1, title: "hello", description: "desc", created_at: "t", updated_at: "u" }],
      })
      .mockResolvedValueOnce({
        next: null,
        previous: null,
        results: [{ id: 2, title: "new", description: "d", created_at: "t", updated_at: "u" }],
      });

    renderWithQuery(<App />);

    // wait initial load
    await screen.findByText("hello");

    fireEvent.change(screen.getByPlaceholderText("title"), { target: { value: "new" } });
    fireEvent.change(screen.getByPlaceholderText("description"), { target: { value: "d" } });

    await user.click(screen.getByRole("button", { name: "Create" }));

    await screen.findByText("new");
  });

  test("shows error when list fails", async () => {
    jest.spyOn(itemsApi, "listItemsCursor").mockRejectedValue(new Error("Network error"));

    renderWithQuery(<App />);

    expect(await screen.findByText("Network error")).toBeInTheDocument();
  });
});
