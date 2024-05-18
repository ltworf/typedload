[THE PROJECT MIGRATED TO CODEBERG](https://ltworf.codeberg.page/typedload/)

typedload's origin story
========================

At $DAYJOB there was a software written in Scala, that worked by mapping objects into mongodb data.

The only one person there knowing Scala decided to quit, and so we were in the process of rewriting the entire thing in Python.

I had been tasked to write a few hundreds methods `to_json()` and `from_json()` for all the various objects that are used by this software.

Since I thought it was going to be a terribly boring job in which I'd make tens of typos, I looked for a library that did such a thing. But of course none existed, so I started writing a module to do that.

The `to_json()` part was rather easy, while the opposite wasn't, anyway after a few days the module seemed to be working nice.

The module in fact worked so nicely that I wanted to use it in my personal projects as well. However I couldn't, as I had written it at $DAYJOB and I knew that getting the authorization to release it as open source would take from 2 years to +∞.

So, I just wrote a stand alone library outside of work to do the exact same thing, but in a more generic and flexible way, rather than tied to the specific software we had at $DAYJOB.

The result of writing the same library twice was that the second time around it came out better, and so the original version got completely discarded and at $DAYJOB typedload is now in use.

At the time pydantic existed but it was not available on any distribution and was not production quality.
