# EvenTDT

EvenTDT is a library six years in the making.
Originally, EvenTDT started as a library to implement event tracking, or Topic Detection and Tracking (TDT), algorithms.
Over the course of my studies, however, it has organically developed into a behemoth of a system that provides the basis for many event-related tasks.

> To replicate [the PhD analyses](https://github.com/NicholasMamo/phd-data), you can open the files and examine the `cmd._cmd` entries. 

## How to use this library

The library has three main sections: the documentation, the actual EvenTDT library and associated tools.

- The documentation includes extensive instructions on how to use the library and its tools.
While the structure is in the `docsource/` folder, the library fetches the documentation from the library's in-line code.
To compile the documentation, run  `python -m sphinx docsource docs` from the command-line, and then open the `docs/` folder using a browser.
- The actual EvenTDT library, in `eventdt/` is divided into topics.
Arguably, the `queues.consumers`  module contains the most important classes, which consume tweet corpora and detect topics from events.
- The associated tools, in the `tools/` folder, make it easier to use the EvenTDT library.
All tools provide a command-line interface.

## Sample use-cases

While EvenTDT's scope is large, you will probably be using three tools.

- The `collect` tool lets you collect tweet datasets.
To collect corpora, first copy the configuration file from `config/example.py` into `config/conf.py` and enter your credentials.
The `collect` tool supports both versions of the Twitter API—1.1 and 2—and connects to both the sample and filter endpoints.
- The `consume` tool lets you detect events from tweet corpora.
You can, for example, use the `consume` tool to detect events using SEER.
Note that apart from the input corpora, some algorithms may also require other parameters, which can be provided from the command-line.
- The `summarize` tool summarizes timelines.
EvenTDT's algorithms produce JSON-encoded timelines with tweets that describe topics.
To create a readable summary, use the `summarize` tool.

More detailed instructions for the above tools and others, including an exhaustive list of accepted parameters, can be viewed using the `--help` parameter; for example, `tools/consume.py --help`.
You can also read a formatted version of each tool's instructions from the documentation.
The documentation includes the output formats.

## How to extend this library

EvenTDT has been designed with extinsibility in mind.
Packages such as `twitter` include general functions that you can use with tweet corpora, and most other packages include base classes to facilitate the development of novel algorithms.
The following instructions describe how you would develop a new event tracking or TDT algorithm, but the same principles apply for all other techniques, such as summarization methods.

1. Find the base classes.
For example, you can extend the `queues.consumers.Consumer` if you are implementing a real-time TDT algorithm, and the `queues.consumers.buffered_consumer.BufferedConsumer` if you are implementing an algorithm that processes tweets in batches or time windows.
Pay attention to the structure—the expected inputs and outputs—and implement all abstract methods.
2. Add unit tests for the algorithms.
All tests reside in the `tests/` folder in each package and sub-module.
Then, add the algorithm's tests to the general test script, `tests.sh` and add.
3. Add the class to the documentation.
The documentation resides in the `docsource/` folder.
Add the class to the correct file.
4. Add the new algorithm to the right tool.
For example, you can add a TDT consumer to the `consume` tool.
Make sure to add support for any important parameters.

> Note the distinction between the `tdt` and `queues.consumers` packages.
> Use the `tdt` package to implement the core TDT algorithm, such as the logic that looks for bursts.
> Use the `queues.consumers` package to implement the broader process that surrounds the TDT algorithm: pre-processing, filtering and so on.

You can contribute your novel algorithm to EvenTDT by making a pull request.
However, requests that do not follow EvenTDT's structure closely will be rejected.

You can still use EvenTDT if you prefer to use a different structure.
Simply fork the repository and add your contributions there.

## Citing EvenTDT

If you use in this repository, cite the following thesis:

> Mamo, N. Reading Between Events: Exploring the Role of Machine Understanding in Event Tracking. PhD thesis, Department of Artificial Intelligence, Faculty of Information & Communication Technology, University of Malta, XYZ 2022.