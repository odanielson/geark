geark
=====

** Current status: Unstable lab state, only parts of greenletmanager
implemented. **

Geark is a python gevent based library that provides a few functionalities
for building greenlet-queue based applications with gevent.

It aims to provide

 - A Greenletmanager which can be used to start, stop and monitor greenlets
 - A QueueManager that can be used to access named Queues
 - A DashboardInfo that can be used to represent the application functionality
   on a high level perspective.
 - A Dashboard application that can be used to monitor the DashboardInfo for a
   running application
