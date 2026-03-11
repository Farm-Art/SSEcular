# SSEcular
A backend-agnostic, sync/async capable Server Sent Events client for Python 3

## Motivation

I needed an SSE client for a quick and dirty personal script. After trying multiple available packages, I was left unsatisfied and decided to implement [my own](https://xkcd.com/927/), both as a tool I would use and an exercise in recreational programming.

Implementation is based on [the SSE spec](https://html.spec.whatwg.org/multipage/server-sent-events.html).

## Goals

* No dependencies.
* Simple interface that works in dirty scripts as well as proper projects.
* Backend-agnostic, flexible design. Easy-to-implement custom backends.
* Built-in support for most popular request libraries: `httpx`, `requests`, `aiohttp`, maybe others?

## Current state

Early design stage. Toying with different approaches to API layout.
