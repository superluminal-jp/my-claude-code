# DADS components by format

Which of the 43 components of the DADS HTML components (tag `v20261118`) suit each format. "Limited" means the use in the last column only.

| Component | Slides | Page | Use |
|---|---|---|---|
| `heading` | Yes | Yes | Titles and levels |
| `list` | Yes | Yes | Bulleted and numbered text |
| `description-list` | Yes | Yes | Terms with their explanations |
| `table` | Yes | Yes | Comparison. On slides, the static samples only |
| `blockquote` | Yes | Yes | A quotation with its source |
| `notice-block` | Yes | Yes | A note or caution |
| `chip-label` | Yes | Yes | A status or category label |
| `divider` | Yes | Yes | A rule between blocks |
| `image` | Yes | Yes | A figure with a caption |
| `link` | Yes | Yes | A reference |
| `step-navigation` | Yes | Yes | The steps of a procedure |
| `notification-banner` | Limited | Yes | Emphasis. On slides, without the close button |
| `resource-list` | Limited | Yes | A list of sources. On slides, a few items |
| `toc` | Limited | Yes | On slides, one agenda slide |
| `breadcrumb` | Limited | Limited | Position within chapters, or within several pages |
| `button` | Limited | Limited | A call to action that is a link |
| `accordion` | No | Yes | Detail that may stay closed |
| `disclosure` | No | Yes | Detail that may stay closed |
| `tab` | No | Limited | Alternatives shown one at a time |
| `page-navigation` | No | Limited | Material of several pages |
| `horizontal-menu` | No | Limited | Material of several pages |
| `menu-list` | No | Limited | A side menu for several pages |

Not used in either format:

- `card`: the samples have a fixed width in `px` and are links. Use `deck-panel`.
- `carousel`, `modal-dialog`: hide content until operated.
- `drawer`, `hamburger-menu-button`, `menu-list-box`, `language-selector`, `utility-link`, `search-box`: navigation of a website.
- `emergency-banner`: reserved for emergencies.
- `progress-indicator`: shows that something is loading.
- `checkbox`, `radio`, `input-text`, `textarea`, `select`, `switch`, `date-picker`, `calendar`, `file-upload`, `form-control-label`: form input.

DADS has no component for a slide layout, columns, a code block, a tree diagram, or a chart. The first four are in `deck.css`; a chart needs its own solution.
