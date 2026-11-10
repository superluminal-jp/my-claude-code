# Structurizr DSL workspaces

Use Structurizr DSL when the repository already keeps a Structurizr workspace,
or the user asks for a model from which the views are generated: the model
(elements and relationships) is written once in a workspace, and each view is
a selection from it, so a name changed in the model changes in every view.
The cost is a rendering step, because no Markdown host renders the DSL
itself; the number of views alone does not justify it, since Mermaid views
stay consistent when each element keeps one id and one name.

## Workspace shape

Start from `assets/templates/workspace.dsl`, which passes the checker.

```text
workspace "<name>" "<description>" {
    model {
        member = person "<name>" "<description>"
        sys = softwareSystem "<name>" "<description>" {
            api = container "<name>" "<description>" "<technology>"
        }
        member -> api "<what and why>" "<protocol>"
    }
    views {
        systemContext sys "context" "<view description>" {
            include *
            autoLayout lr
        }
    }
}
```

Syntax from the DSL language reference:

| Statement | Syntax |
|---|---|
| Person | `person <name> [description] [tags]` |
| Software system | `softwareSystem <name> [description] [tags]` |
| Container | `container <name> [description] [technology] [tags]` |
| Relationship | `<identifier> -> <identifier> [description] [technology] [tags]` |
| System context view | `systemContext <software system identifier> [key] [description]` |
| Container view | `container <software system identifier> [key] [description]` |
| Dynamic view | `dynamic <*\|software system identifier\|container identifier> [key] [description]` |
| Deployment view | `deployment <*\|software system identifier> <environment> [key] [description]` |
| Inside a view | `title <title>` overrides the view's title; `description <description>`; `autoLayout [tb\|bt\|lr\|rl]` |

Give every element its description (and every container and component its
technology) and every relationship its description and protocol; the checker
reports any that are missing.

## Rendering to pages

The Structurizr documentation lists exporters to PlantUML, C4-PlantUML,
Mermaid, and other formats. Running them needs Structurizr's own tooling,
which is downloaded software: ask before installing or running it. After
exporting a view to Mermaid, paste it into a page made from
`assets/templates/view-page.md`, add `accTitle` and `accDescr`, and run the
checker, because the page rules (title, lead, legend, element table) are not
part of the export.

If the tooling cannot be used, keep `workspace.dsl` as the source of names
and draw each view in Mermaid by hand from it, with the same ids.

## Sources

- DSL language reference: <https://docs.structurizr.com/dsl/language>
- DSL tutorial (workspace, model, views): <https://docs.structurizr.com/dsl/tutorial>
- DSL overview and exporters: <https://docs.structurizr.com/dsl>
