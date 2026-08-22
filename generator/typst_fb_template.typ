#let margin = 0cm
#let background_enabled = true

#let data = json("data.json")
#let img_path_prefix = "pic"

#let months_title = if "months" in data {
  data.months
} else if "title" in data {
  data.title
} else if "left_month" in data and "right_month" in data {
  data.left_month + " & " + data.right_month
} else {
  "April & Maj"
}

#set page(
  paper: "a4",
  flipped: true,
  margin: margin
)

#let text_color = if background_enabled { white } else { gray.darken(60%) }
#let qr_color = if background_enabled { rgb(10, 100, 10) } else { gray.darken(60%) }


#set text(
  lang: "da",
  fill: text_color,
  size: 24pt,
)

// Lav billederne med prepare_image.sh scriptet, som laver blur og mørkere versioner af billedet.

#if background_enabled {
  place(box(image(img_path_prefix + ".jpg", width: 29.7cm - 2*margin, height: 21cm - 2*margin)))
  place(box(image(img_path_prefix + " blur dark.jpg", width: 29.7cm - 2*margin, height: 21cm - 2*margin), outset: (top: -4.5cm, right: -3.5cm, left: -3.5cm, bottom: -4cm), radius: 30pt, clip: true)) // todo fix this should be automated
}

// fix placement if emojies
// and ignore outer grid
#show grid: it => {
  if it.align == (right, left) {
    return it
  }
  
  show grid.cell.where(x: 1): it => {  
    place(dx: 4pt, dy: -4pt, it)
  }
  
  it
}

#let show_element = e => {
  (
    e.date,
    e.emoji,
    [#set par(leading: 6pt)
      #e.title #if e.description != "" {
      v(-18pt)
      set par(leading: 9pt)
      text(size: 11pt, e.description)
    }],
  )
}

#box(
  width: 29.7cm - 2*margin, 
  height: 21cm - 2*margin, 
  inset: (x: 3.8cm, y: 3cm))[
  #align(center, text(size: 42pt, smallcaps[*#months_title*]))
  #v(-0.5cm)
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 6pt,
    align: (right, left),
    grid(
      columns: (2.5cm, 1.3cm, 1fr), 
      align: (right, center, left),
      row-gutter: 0.7cm,
      .. for e in data.left {
        show_element(e)
      }
    ),
    grid(
      columns: (2.5cm, 1.3cm, 1fr), 
      align: (right, center, left),
      row-gutter: 0.7cm,
      .. for e in data.right {
        show_element(e)
      }
    ),
  )<ignore>
]

#import "@preview/tiaoma:0.3.0": qrcode, micro-qr


#place(right, dy:-3.7cm, dx:-0.7cm, [#place(dy: 64pt, dx: -4.6cm)[E26 program] #box(radius: 12pt, clip: true, inset: 6pt, fill: white, qrcode("https://docs.google.com/document/d/1Q0a5lNur4xGYu4U55zu0fPPnNbwAqoWH/edit", options: (scale: 1.5, fg-color: qr_color)))])

