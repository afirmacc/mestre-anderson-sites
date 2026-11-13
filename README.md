# Mestre Anderson — Especialista em desenvolvimento de sites

Skill pública para agentes que concebem, desenvolvem, melhoram e auditam sites. Reúne práticas de experiência, identidade visual, acessibilidade, desempenho, SEO/GEO, Analytics e conversão, com atenção à jornada real de quem usa o produto.

## Instalação no Codex

Clone este repositório na pasta de skills:

```bash
git clone https://github.com/afirmacc/mestre-anderson-sites.git ~/.codex/skills/mestre-anderson-sites
```

Reinicie o Codex se a skill não aparecer imediatamente. Para usá-la de forma explícita, peça: `$mestre-anderson-sites`.

## Conteúdo

- [`SKILL.md`](SKILL.md): instruções de trabalho do especialista.
- [`references/caso-combinado.md`](references/caso-combinado.md): lições do projeto Combinado em Família. É um estudo de caso, não um conjunto de regras para outros produtos.
- [`scripts/audit_public_site.py`](scripts/audit_public_site.py): verificação inicial de páginas listadas em um sitemap.

Exemplo de auditoria:

```bash
python3 scripts/audit_public_site.py https://seu-dominio.example
```

O script e as notas automáticas são pontos de partida. Confira achados importantes no navegador, no código e com dados reais antes de concluir uma auditoria.

## Contribuições

Sugestões e correções são bem-vindas por issues e pull requests. Ao compartilhar um caso, remova dados pessoais, credenciais e informações internas. Prefira fontes oficiais para recomendações que possam mudar com o tempo.

## Licença

MIT. Consulte [`LICENSE`](LICENSE).
