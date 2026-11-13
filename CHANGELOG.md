# Histórico de versões

## 0.1.2

- Define a manutenção conjunta para Codex e Claude Code, com commits por melhoria, tags e reversão que preserva o histórico.
- Adiciona proveniência de cada mudança: pessoa responsável, ferramenta de implementação e ferramenta de revisão.
- Verificação: validadores do Codex e Claude Code; leitura dos caminhos de instalação e do procedimento de reversão.
- Condução: Anderson Oliveira. Implementação: Codex desktop. Revisão: Claude Code CLI (somente leitura; ajustes de rollback e proveniência incorporados).

## 0.1.1

- Torna o auditor de sitemap tolerante a URLs inválidas, aceita IRI e canônicas relativas, lê sitemaps gzip e bloqueia redirecionamentos externos.
- Acrescenta testes locais e reduz detalhes de produção no estudo de caso público.
- Verificação: cinco testes locais, validadores do Codex e Claude Code e amostra de cinco páginas de um sitemap com 69 URLs.
- Condução: Anderson Oliveira. Implementação: Codex desktop. Revisão: Claude Code CLI (análise de leitura; correções confirmadas por testes).

## 0.1.0

- Publica o plugin do Claude Code com comando `/mestre-anderson-sites:site` e instalação por marketplace, preservando a skill do Codex.
- Verificação: instalação isolada pelo marketplace e inventário do plugin com uma skill.
- Condução: Anderson Oliveira. Implementação: Codex desktop. Validação: CLI do Claude Code; sem revisão pelo modelo nessa versão.

## 0.0.1 — base anterior ao plugin

- Commit `d2c8ee0`: primeira skill do Codex. Condução: Anderson Oliveira. Implementação: Codex desktop.
