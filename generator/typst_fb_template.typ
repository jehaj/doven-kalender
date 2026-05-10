#let margin = 0cm
#let background_enabled = true

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

// Lav billederne med vips
// $ vips gaussblur efterår.jpg "efterår blur.jpg" 40
// $ vips linear "efterår blur.jpg" "efterår blur dark.jpg" 0.9 0

#if background_enabled {
  place(box(image("f.jpg", width: 29.7cm - 2*margin, height: 21cm - 2*margin)))
  place(box(image("f blur dark.jpg", width: 29.7cm - 2*margin, height: 21cm - 2*margin), outset: (top: -4.5cm, right: -3.5cm, left: -3.5cm, bottom: -4cm), radius: 30pt, clip: true))
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

#box(
  width: 29.7cm - 2*margin, 
  height: 21cm - 2*margin, 
  inset: (x: 3.8cm, y: 3cm))[
  #align(center, text(size: 42pt, smallcaps[*April & Maj*]))
  #v(-0.5cm)
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 6pt,
    align: (right, left),
    grid(
      columns: (2.5cm, 1.2cm, 1fr), 
      align: (right, center, left),
      row-gutter: 0.7cm,
      [9\. apr],
      [🎤],
      [Lovsangsaften \ #text(size: 16pt, [Fælles med byens IMUer])],
      [14\. apr],
      [📖],
      [#set par(leading: 11pt) 
      Taleraften\ #text(size: 16pt, [Fælles med Reload ved \ *Leif Andersen*: Troshistorie])],
      [16\. apr],
      [#emoji.discoball],
      [Socialaften],
      [23\. apr],
      [#emoji.house],
      [#set par(leading: 11pt) 
      Taleraften\ #text(size: 16pt, [*Peter Mikkelsen* »Menneskemøder i hverdagen«])],
      [30\. apr],
      [#emoji.house.multiple],
      [Smågrupper],
    ),
    grid(
      columns: (2.5cm, 1.2cm, 1fr), 
      align: (right, center, left),
      row-gutter: 0.7cm,
      [7\. maj],
      [#emoji.book.open],
      [Taleraften\ #text(size: 16pt, [Fælles med Reload])],
      [14\. maj],
      [#emoji.discoball],
      [Socialaften \ #text(size: 16pt, [ved *Jakob Larsen*])],
      [21\. maj],
      [#emoji.house],
      [#set par(leading: 11pt) 
      Taleraften\ #text(size: 16pt, [*Irene Christiansen*]) \ #text(size: 11pt, [»Helbredelse---En personlig fortælling om Guds helbredende kraft«])],
      [28\. maj],
      [#emoji.house.multiple],
      [Smågrupper],
    ),
  )<ignore>
]

#import "@preview/tiaoma:0.3.0": qrcode, micro-qr


#place(right, dy:-3.7cm, dx:-0.7cm, [#place(dy: 64pt, dx: -4.6cm)[F26 program] #box(radius: 12pt, clip: true, inset: 6pt, fill: white, qrcode("https://docs.google.com/document/d/1EbI4ZyldB06EyZN_f0kKo4fRHxHSVXa8/edit", options: (scale: 1.5, fg-color: qr_color)))])

