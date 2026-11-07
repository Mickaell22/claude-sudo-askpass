# claude-sudo-askpass

Ventana de contraseña para cuando Claude Code necesita `sudo`. Claude corre sin
terminal interactiva, asi que usa `sudo -A`, y `sudo` llama a este script via
`SUDO_ASKPASS`. Cada vez muestra un titulo distinto sacado de `frases.txt`.

En Wayland con kitty abre una ventana con efectos (`askpass.py`, solo stdlib):
una intro al azar (matrix, maquina de escribir, hackeo falso, estrellas, gatito,
texto arcoiris), un sonido sintetizado distinto cada vez (via `pw-play`), la
contraseña enmascarada con simbolos de colores y, con 8% de probabilidad, un
susto. Toma el color del acento de `~/.config/waybar/accent.css` si existe.
Si no hay Wayland/kitty o algo falla, cae a `zenity`.

La contraseña pasa por un archivo en un directorio `0700` dentro de
`$XDG_RUNTIME_DIR` (tmpfs) y se borra apenas se entrega a sudo.

## Instalar

Requiere `zenity` (respaldo). Para los efectos: `kitty`, `python3` y `pw-play` (PipeWire).

En Hyprland conviene que la ventana flote centrada:

```
windowrule = float on, match:class ^(sudo-askpass)$
windowrule = size 760 440, match:class ^(sudo-askpass)$
windowrule = center on, match:class ^(sudo-askpass)$
```

```sh
ln -sf "$PWD/sudo-askpass" ~/.local/bin/sudo-askpass
```

Y en `~/.claude/settings.json`:

```json
{ "env": { "SUDO_ASKPASS": "/home/<usuario>/.local/bin/sudo-askpass" } }
```

## Agregar frases

Una por linea en `frases.txt`. Se elige una al azar con `shuf`.
