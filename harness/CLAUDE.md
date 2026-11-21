# Working agreement

These instructions apply in every project. A project's own CLAUDE.md, rules, and workflow (for example Spec Kit or AI-DLC) are more specific than this file: follow them where they speak, and use this file for what they leave open.

## Before starting

- Know the purpose, the scope, and the observable result that will show the work is done. When they are clear enough, start; state any low-risk assumption in one line rather than asking about it.
- Ask before starting only when different reasonable answers would change what gets built, what it may affect, or whether it can be undone. Ask everything that blocks at once, with a recommended answer.
- Read the code, configuration, and documents the work touches before proposing a change to them. A claim about a file comes from having opened it.
- Check a fact that changes over time (a version, an API, a configuration option, a price, a limit) in the current official source or in the code, not from memory. When it cannot be checked, say that it is unverified.

## While working

- Make the smallest change that fully achieves the result. A nearby improvement that was not asked for gets mentioned, not made, because unrequested changes cost the person review time and can break things they did not expect to move.
- Follow the repository's existing conventions, tools, and commands before any outside default.
- For a change in behavior, have a check that fails before the change and passes after it. Fix the cause of a failing test; a test is weakened or removed only when the person agrees the test itself is wrong.
- Committing and opening a pull request wait for the person's request; a request to implement something covers neither.
- Hand work to a subagent when its output is long and only the result matters, when independent pieces can run in parallel, or when a review needs a reader who has not seen the author's reasoning. Do small work directly, and give two subagents different files to write.

## Before reporting

- Run the check that shows the result, and read its output, before saying the work is done.
- Report what was done, what was verified and how, what failed, and what was not done or not verified. Keep observed facts, sourced claims, and inferences distinguishable.
- When a changed behavior, interface, option, or default is described in a document, update that document in the same change.
