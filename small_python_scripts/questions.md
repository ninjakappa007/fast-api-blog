1. **Write a retry decorator**

```python
@retry(times=3, delay=1)
def api_call():
    ...
```

Requirements:

* Retry on exception
* Configurable retries
* Optional delay
* Preserve function metadata

---

2. **Implement your own `lru_cache` decorator**

```python
@cache
def fib(n):
    ...
```

Requirements:

* Cache based on args
* Limit cache size
* Evict oldest entries

---

3. **Build a custom JSON serializer**

```python
to_json({
    "a": 1,
    "b": [1,2,3]
})
```

Do not use `json.dumps`

Handle:

* dict
* list
* string
* bool
* int
* None

---

4. **Create a mini task scheduler**

```python
scheduler.add(task, delay=5)
scheduler.run()
```

Requirements:

* Execute functions after delay
* Use threads or async
* Handle multiple tasks

---

5. **Implement a context manager**

```python
with Timer():
    slow_function()
```

Requirements:

* Measure execution time
* Use both:

  * class-based
  * `contextlib`

---

6. **Build a thread-safe counter**

```python
counter.increment()
counter.value()
```

Requirements:

* Multiple threads
* No race condition
* Use `Lock`

---

7. **Write your own `flatten()` generator**

```python
list(flatten([1,[2,[3,4]],5]))
```

Requirements:

* Recursive
* Use `yield from`
* Support tuples + lists

---

8. **Create a rate limiter decorator**

```python
@rate_limit(calls=5, per=60)
def send():
    ...
```

Requirements:

* Allow only N calls per time window
* Raise exception otherwise

---

9. **Implement a simple ORM-like model**

```python
class User(Model):
    name = StringField()
    age = IntField()
```

Requirements:

* Use metaclasses or descriptors
* Validate types
* Store schema info

---

10. **Build a mini pytest**

```python
@test
def test_add():
    assert add(1,2) == 3
```

Requirements:

* Auto discover test functions
* Run tests
* Print pass/fail summary

---

High-value topics these cover:

* decorators
* closures
* generators
* threading
* metaclasses
* descriptors
* context managers
* caching
* concurrency
* introspection
* function wrapping
* clean architecture

These are closer to real SDET/backend interview coding than standard DSA.
