# Delegating to subagents

Claude Code's subagent documentation is the authority on what a subagent is and how one is configured. The points below are how to use them well.

- Delegate for one of three reasons: the output is long and only the result matters (a test run, a build, a wide search); independent pieces can run in parallel; or a review needs a reader who has not seen the author's reasoning. Do everything else directly, because a subagent starts with no context, costs a full run, and returns less detail than it saw.
- Write the brief for a reader who knows nothing of this conversation: the goal and what done looks like, what is already known or ruled out, the files to read (paths, not retyped content), what is in scope and what must not be touched, and the form of the answer.
- Ask for evidence in the answer, not conclusions alone: each command with its exit code and the verbatim text of any failure, each finding with `path:line`.
- Use the least that does the job: the built-in search agent for a search, a cheaper model for mechanical work such as running checks, a read-only agent for a review.
- For a review, hand over the files and the question, not your own conclusion; an agent given a hypothesis tends to confirm it.
- Give two subagents different files to write, and do not redo delegated work yourself while it runs.
- Treat a report as claims. Check what a decision depends on before relying on it; whether the work is complete is judged here, not by the subagent.
