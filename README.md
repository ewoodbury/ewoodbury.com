# ewoodbury.com
Personal site and blog

[ewoodbury.com](https://ewoodbury.com)

# Setup

- Themes live in `/themes` (etch plus hugo-shortcode-gallery for the photo page).

- Posts are page bundles: `content/posts/<slug>/index.md`, with images next to the post. `hugo new posts/<slug>` creates that layout.

- Run `hugo server`. Open `localhost:1313` to view the site.

- Production builds include GoatCounter (`params.goatcounter.code` in `config.toml`). The dashboard is at `https://<code>.goatcounter.com`. Leave `code` empty to disable the snippet.
