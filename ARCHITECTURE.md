Dette dokument beskriver en ide til projektets arkitektur.

Figuren nedenfor beskriver det overordnet.

```d2
Google Kalender

dovenKalender: {
  kalender
  poster: {
    api
    manual
    selenium
  }
  generator: {
    ollama
    chatgpt
    lechat
  }
}

Google Kalender <- dovenKalender.kalender
dovenKalender.kalender -> dovenKalender.generator -> dovenKalender.poster

dovenKalender.poster -> Facebook
```

> [!NOTE]
> Det ser ikke ud til, at der er en smart måde at vise det i Markdown. Man kan gå ind på 
> [play.d2lang.com](https://play.d2lang.com) og indsætte koden der for at få figuren vist. Man kunne bruge MermaidJS i 
> stedet for, det virker både i GitHub, VSCode og Jetbrains produkter.
