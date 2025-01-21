import { RefObject, useEffect } from "react";

export const useClickOutside = (
  ref: RefObject<HTMLElement>,
  callback: () => void,
) => {
  const handleClick = (event: MouseEvent) => {
    if (
      ref !== null &&
      ref.current &&
      !ref.current.contains(event.target as HTMLElement)
    ) {
      callback();
    }
  };

  useEffect(() => {
    document.addEventListener("click", handleClick);

    return () => {
      document.removeEventListener("click", handleClick);
    };
  });
};
