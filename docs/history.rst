.. _history:

===============================
The history of Locust
===============================

Locust was created because we were fed up with existing solutions. None of them are solving the 
right problem and to me, they are missing the point. We've tried both Apache JMeter and Tsung. 
Both tools are quite OK to use; we've used the former many times benchmarking stuff at work.
JMeter comes with a UI, which you might think for a second is a good thing. But you soon realize it's
a PITA to "code" your testing scenarios through some point-and-click interface. Secondly, JMeter 
is thread-bound. This means for every user you want to simulate, you need a separate thread. 
Needless to say, benchmarking thousands of users on a single machine just isn't feasible.

Tsung, on the other hand, does not have these thread issues as it's written in Erlang. It can make 
use of the light-weight processes offered by BEAM itself and happily scale up. But when it comes to 
defining the test scenarios, Tsung is as limited as JMeter. It offers an XML-based DSL to define how 
a user should behave when testing. I guess you can imagine the horror of "coding" this. Displaying 
any sorts of graphs or reports when completed requires you to post-process the log files generated from
the test. Only then can you get an understanding of how the test went.

Anyway, we've tried to address these issues when creating Locust. Hopefully none of the above 
pain points should exist.

I guess you could say we're really just trying to scratch our own itch here. We hope others will 
find it as useful as we do.

- `Jonatan Heyman <http://heyman.info>`_ (`@jonatanheyman <https://twitter.com/jonatanheyman>`_ on Twitter)
