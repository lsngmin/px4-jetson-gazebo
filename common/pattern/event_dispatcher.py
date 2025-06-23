from __future__ import annotations

import asyncio, logging
from collections import defaultdict
from typing import Callable, Any, Awaitable
from collections import defaultdict
from threading import RLock
import weakref
from typing import Callable, DefaultDict, Dict, List, Protocol, TypeVar, Any
from common.pattern.singleton import Singleton

T = TypeVar("T")

class EventDispatcher:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, msg_type, callback):
        self._subscribers[msg_type].append(callback)

    def publish(self, msg):
        for cb in self._subscribers[msg.get_type()]:
            cb(msg)


class _Subscriber(Protocol[T]):
    def __call__(self, event: T) -> None: ...


class MEventDispatcher:
    _instance: "MEventDispatcher | None" = None
    _lock = RLock()

    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[weakref.ReferenceType]] = defaultdict(list)

    def subscribe(self, topic: str, callback: _Subscriber[Any]) -> None:
        ref = (weakref.WeakMethod(callback) if hasattr(callback, "__self__")
               else weakref.ref(callback))
        with self._lock:
            self._subs[topic].append(ref)

    def unsubscribe(self, topic: str, callback: _Subscriber[Any]) -> None:
        with self._lock:
            self._subs[topic] = [
                r for r in self._subs[topic] if r() is not callback
            ]

    def publish(self, topic: str, event: Any = None) -> None:
        with self._lock:
            refs = list(self._subs[topic])      # shallow copy
        dead: List[weakref.ReferenceType] = []
        for ref in refs:
            cb = ref()
            if cb is None:
                dead.append(ref)
            else:
                try:
                    cb(event)
                except Exception as e:
                    print(f"[EventBus] {topic} callback error: {e}")
        if dead:
            with self._lock:
                for r in dead:
                    self._subs[topic].remove(r)

    @classmethod
    def instance(cls) -> "MEventDispatcher":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

class M2EventDispatcher:
    _instance: "M2EventDispatcher | None" = None
    _lock = RLock()

    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[weakref.ReferenceType]] = defaultdict(list)

    def subscribe(self, topic: str, callback: _Subscriber[Any]) -> None:
        ref = (weakref.WeakMethod(callback) if hasattr(callback, "__self__")
               else weakref.ref(callback))
        with self._lock:
            self._subs[topic].append(ref)

    def unsubscribe(self, topic: str, callback: _Subscriber[Any]) -> None:
        with self._lock:
            self._subs[topic] = [
                r for r in self._subs[topic] if r() is not callback
            ]

    def publish(self, topic: str, event: Any = None) -> None:
        with self._lock:
            refs = list(self._subs[topic])      # shallow copy
        dead: List[weakref.ReferenceType] = []
        for ref in refs:
            cb = ref()
            if cb is None:
                dead.append(ref)
            else:
                try:
                    cb(event)
                except Exception as e:
                    print(f"[EventBus] {topic} callback error: {e}")
        if dead:
            with self._lock:
                for r in dead:
                    self._subs[topic].remove(r)

    @classmethod
    def instance(cls) -> "M2EventDispatcher":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
