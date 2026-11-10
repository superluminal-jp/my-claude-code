# <View type>: <scope>

<One to three sentences that answer this view's question in words the reader
already uses: what the reader learns from the diagram below.>

```mermaid
flowchart LR
  accTitle: <View type>: <scope>
  accDescr: <One or two sentences saying what the diagram shows, readable without the picture.>
  person1(["<Role name><br/>[Person]<br/><What they do with the system>"]):::person
  system1["<System name><br/>[Software System]<br/><What it is responsible for>"]:::system
  external1["<System name><br/>[Software System: external]<br/><What it does for this system>"]:::external
  person1 -->|"<What they ask for and why>"| system1
  system1 -->|"<What it asks for and why><br/>[<protocol>]"| external1
  classDef person fill:#CFE0F3,stroke:#1F4E79,color:#0B1F33
  classDef system fill:#DCE9F7,stroke:#1F4E79,stroke-width:2px,color:#0B1F33
  classDef external fill:#EDEDED,stroke:#4D4D4D,stroke-dasharray:5 3,color:#0B1F33
```

## Legend

| Notation | Meaning |
|---|---|
| Rounded shape | A person, by their role |
| Blue box with a thick border | The system this view is about |
| Grey box with a dashed border | A system outside it, marked "external" |
| Arrow | Who asks whom, in that direction; the label says what and why, and the protocol in brackets |

## Elements

| Name | Type | Responsibility | Technology | Source |
|---|---|---|---|---|
| <Role name> | Person | <...> | — | <file:line, document, or "user"> |
| <System name> | Software System | <...> | <...> | <...> |

## Assumptions and open questions

- <Anything drawn without a source, and anything that could not be determined.>

## Related views

- Index: [Architecture diagrams: <system>](index.md)
- Up and down: <links to the views one level out and one level in>

