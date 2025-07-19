from typing import Any, Dict, List


class Reducer:
    """
    Reducer class for handling field-level state updates in LangGraph

    This class provides static methods that act as reducers,
    for updatingvstate variables across workflow nodes in a controlled and consistent way
    """
    @staticmethod
    def update(current: Any, new: Any) -> Any:
        """
        Replace the current value if the new one is valid

        Args:
            current (Any): The existing value
            new (Any): The new value to possibly replace the current one

        Returns:
            Any: The updated value if valid; otherwise, the original
        """
        if new is None or new == {}:
            return current
        return new

    @staticmethod
    def append_and_trim(current: List[Any], new: List[Any], max_length: int) -> List[Any]:
        """
        Appends new entries and keeps only last n no. of items

        Args:
            current (List[Any]): The existing list of items
            new (List[Any]): The list of new items to append
            max_length (int): The maximum allowed length of the list

        Returns:
            List[Any]: The updated and trimmed list
        """
        if current is None:
            current = []
        if not new:
            new = current
        if current and new[-1] == current[-1]:
            return current
        current.extend(new)
        return current[-max_length:]

    @staticmethod
    def increment_one(current: int, new: int) -> int:
        """
        Increments the value by one or resets

        Args:
            current (int): The existing counter value
            new (int): If 1, increment the counter; if 0, reset it

        Returns:
            int: The updated counter value
        """
        if new == 1:
            return current + 1
        if new == 0:
            return 0
        return current

    @staticmethod
    def merge_dicts(current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges new key-value pairs into existing dictionary

        Args:
            current (Dict[str, Any]): The original dictionary
            new (Dict[str, Any]): The dictionary containing updates

        Returns:
            Dict[str, Any]: The merged dictionary
        """
        if current is None:
            current = {}
        current.update(new)
        return current
