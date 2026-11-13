# Mestre Anderson — Especialista em desenvolvimento de sites

Skill pública para agentes que concebem, desenvolvem, melhoram e auditam sites. Reúne práticas de experiência, identidade visual, acessibilidade, desempenho, SEO/GEO, Analytics e conversão, com atenção à jornada real de quem usa o produto.

## Instalação no Codex

Clone este repositório na pasta de skills:

```bash
git clone https://github.com/afirmacc/mestre-anderson-sites.git ~/.codex/skills/mestre-anderson-sites
```

Reinicie o Codex se a skill não aparecer imediatamente. Para usá-la de forma explícita, peça: `$mestre-anderson-sites`.

## Instalação no Claude Code

No Claude Code 2.1.275 ou superior, instale diretamente do marketplace deste repositório:

```text
/plugin install mestre-anderson-sites --marketplace afirmacc/mestre-anderson-sites
```

Também é possível usar o terminal:

```bash
claude plugin marketplace add afirmacc/mestre-anderson-sites
claude plugin install mestre-anderson-sites@afirmacc
```

Para trabalhar com uma cópia local ligada ao SourceTree, clone o repositório na pasta de skills do Claude Code:

```bash
git clone https://github.com/afirmacc/mestre-anderson-sites.git ~/.claude/skills/mestre-anderson-sites
```

Em uma nova sessão do Claude Code, invoque `/mestre-anderson-sites:site`. O manifesto em `.claude-plugin/plugin.json` faz a mesma pasta funcionar como plugin pessoal no Claude Code. Para conferir a instalação, rode `claude plugin validate ~/.claude/skills/mestre-anderson-sites`, `claude plugin list` e `claude plugin details mestre-anderson-sites@skills-dir`.

Se você já clonou para o Codex no mesmo computador e a pasta de destino ainda não existe, pode criar um link simbólico no lugar de uma segunda cópia:

```bash
ln -s ~/.codex/skills/mestre-anderson-sites ~/.claude/skills/mestre-anderson-sites
```

## Conteúdo

- [`SKILL.md`](SKILL.md): instruções de trabalho do especialista.
- [`references/caso-combinado.md`](references/caso-combinado.md): lições do projeto Combinado em Família. É um estudo de caso, não um conjunto de regras para outros produtos.
- [`scripts/audit_public_site.py`](scripts/audit_public_site.py): verificação inicial de páginas listadas em um sitemap.

Exemplo de auditoria:

```bash
python3 scripts/audit_public_site.py https://seu-dominio.example
```

No Windows, use `py -3` no lugar de `python3`. O script usa apenas a biblioteca padrão do Python 3.9 ou superior. Ele aceita sitemaps XML e `.xml.gz`, limita cada sitemap a 50 MB descompactados e percorre até 100 sitemaps; acima desse limite, informa o erro. Audita até 200 páginas por padrão. Use `--max-pages` para ajustar o corte, `--json` para guardar o relatório e `--fail-on-issues` quando quiser código de saída 1 para problemas, URLs inválidas ou metadados duplicados. Um sitemap indisponível ou sem URLs do site também causa erro explícito.

O script e as notas automáticas são pontos de partida. Confira achados importantes no navegador, no código e com dados reais antes de concluir uma auditoria.

## Contribuições

Sugestões e correções são bem-vindas por issues e pull requests. Ao compartilhar um caso, remova dados pessoais, credenciais e informações internas. Prefira fontes oficiais para recomendações que possam mudar com o tempo.

## Licença

MIT. Consulte [`LICENSE`](LICENSE).
