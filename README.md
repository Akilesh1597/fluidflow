# fluidflow
A communications library for cooperative bots

## Use cases

### Simple Task Execution
Most tasks that are part of more complex procedures have to be executed in a
certain order. Sometimes some of those tasks may be executed concurrently.
There are plenty of graph algorithms to determine the optimal execution order.

Tasks in coalesce use python's async/await syntax to solve a DAG and
execute tasks in concurrent or sequential manner based on their dependencies.
The dependencies can be extablished by the task's metadata. The metadata
defines what data is produced and consumed by the tasks. 

Tasks that consume some data produced by other tasks are chained using python's
Future objects. Tasks that do not depend on other tasks execute concurrently. 

### Retry and Revert
Failures in tasks may trigger a retry or revert logic if one is defined.
The Retry and Revert may also depend on other task's execution and may also 
trigger the Retry and Revert of other tasks.

### Adhoc Tasks
Sometimes tasks(nodes) may have to be included/excluded from the
procedure(graph), depending on the result of some other tasks. 

### Swarm
Tasks sometimes may depend on other tasks, that run remotely. Data produced
by the tasks are shared over a channel(message queues).

### Progress report
Every task, remote or local shall report its progress, both quantitatively
and descriptively to its parent procedure. 

### Crash Recovery
Procedures supporting remote tasks also overcome task crashes. Once a task
is deemed unfit for execution, it is terminated and a new one shall take its
place. Tasks and procedures interface with higher level clustering
softwares (mesosphere, kubernetes) to make the most of the computing
