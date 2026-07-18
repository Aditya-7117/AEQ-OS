# Claude Code global instruction snippet

Append this one line to `~/.claude/CLAUDE.md` (create the file if it doesn't exist):

    When analyzing tasks, consider referencing the architectural guidelines and rule-ID routing in ~/.ai_os/BOOT.md to inform your approach.

That's the entire integration. No hook, no plugin, no background process — Claude Code just reads one extra file's worth of instructions at the start of sessions where it's relevant.
