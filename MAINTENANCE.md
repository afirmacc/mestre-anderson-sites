# Manutenção e histórico

O mesmo checkout pode alimentar a skill do Codex e o plugin do Claude Code: use um link simbólico de `~/.claude/skills/mestre-anderson-sites` para `~/.codex/skills/mestre-anderson-sites`. Assim os dois agentes usam a mesma cópia, e o SourceTree mostra os commits desse repositório. Uma nova sessão ou o recarregamento de plugins aplica mudanças locais.

## Quando incorporar uma melhoria

Ao usar a skill, registre um aprendizado **reutilizável** quando houver evidência de que ele melhora o método, o script ou a compatibilidade. Verifique o comportamento com um caso concreto. Não transforme decisões particulares de um cliente em regras gerais e não publique dados internos.

Para cada mudança coerente:

1. Descreva o problema e o comportamento esperado. Faça a menor correção que o resolve.
2. Valide a skill do Codex (quando o validador estiver disponível) e execute `claude plugin validate --strict .`.
3. Se o script mudou, execute `python3 -B -m unittest discover -s tests -v` e, quando fizer sentido, uma amostra real de site autorizado. Se mudou a invocação, confirme-a em uma sessão nova do agente afetado.
4. Atualize a versão em `.claude-plugin/plugin.json` e registre em `CHANGELOG.md` o que mudou, como foi verificado, quem conduziu a mudança e quais ferramentas implementaram ou revisaram. Use patch para correções, minor para capacidade nova compatível e major para mudança incompatível.
5. Faça **um commit por melhoria coerente**, em português. Mantenha o nome real de quem conduz o trabalho como autor do commit e registre no corpo as ferramentas usadas, com seus papéis. Por exemplo:

   ```text
   Corrige leitura de sitemaps compactados

   Implemented-With: Codex desktop
   Reviewed-With: Claude Code CLI
   ```

   Para uma edição direta sem agente, registre `Implemented-With: manual`; a pessoa responsável aparece como autora do commit. Se não houve revisão por outra ferramenta, omita `Reviewed-With`; não atribua trabalho a quem não participou. Quando várias ferramentas participarem, registre cada uma e seu papel.
6. Depois de validado e autorizado na conversa, envie o commit ao remoto e crie/envie a tag `vX.Y.Z`. Não faça commit de alterações não relacionadas.

Instalações da comunidade podem abrir um pull request. O checkout de manutenção da Afirma pode publicar diretamente quando a conversa autorizar. Esta documentação não concede, por si só, permissão para push.

## Se uma mudança piorar a skill

Use `git log --oneline --decorate` ou o histórico do SourceTree para localizar a última versão boa. Compare com `git diff vX.Y.Z..main`. Para inspecionar sem mexer na cópia ativa, crie um worktree temporário apontando para a tag.

Para corrigir uma regressão já publicada, comece com uma árvore de trabalho limpa. Execute `git revert --no-commit <hash>` (para um merge, `git revert -m 1 --no-commit <hash>`), atualize o número de versão para o próximo patch e registre a reversão no `CHANGELOG.md`. Preserve também as entradas das versões anteriores que o revert possa ter removido do arquivo. Valide e crie **um novo commit**, tag e push. O histórico preserva a tentativa, a falha e a correção. Não use `reset --hard`, force push nem mova ou recrie tags publicadas sem pedido explícito.

As tags `v0.0.1`, `v0.1.0` e `v0.1.1` marcam a primeira skill do Codex, a primeira versão do plugin e a correção inicial do auditor. O histórico completo continua no GitHub. As versões anteriores aos trailers de proveniência estão identificadas no `CHANGELOG.md`, sem reescrever commits já publicados.
