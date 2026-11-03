# claude-sudo-askpass

Ventana de contraseña para cuando Claude Code necesita `sudo`. Claude corre sin
terminal interactiva, asi que usa `sudo -A`, y `sudo` llama a este script via
`SUDO_ASKPASS`. Cada vez muestra un titulo distinto sacado de `frases.txt`.

## Instalar

Requiere `zenity`.

```sh
ln -sf "$PWD/sudo-askpass" ~/.local/bin/sudo-askpass
```

Y en `~/.claude/settings.json`:

```json
{ "env": { "SUDO_ASKPASS": "/home/<usuario>/.local/bin/sudo-askpass" } }
```

## Agregar frases

Una por linea en `frases.txt`. Se elige una al azar con `shuf`.
