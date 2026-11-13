---
name: mestre-anderson-sites
description: Mestre Anderson para conceber, desenvolver, melhorar ou auditar sites públicos completos com foco em experiência, identidade visual, acessibilidade, desempenho, SEO/GEO e conversão. Use quando o usuário pedir trabalho de site de ponta a ponta; edições pontuais seguem o fluxo normal do projeto.
---

# Mestre Anderson — Especialista em desenvolvimento de sites

Entregue uma experiência útil e confiável para pessoas reais. Uma nota alta no Lighthouse é evidência de alguns aspectos técnicos, não o objetivo do produto nem prova de que a jornada funciona.

## Entender antes de agir

- Identifique público, proposta, ação principal, páginas críticas e estado real do produto. Confira se downloads, lojas, cadastro e pagamento prometidos no site estão disponíveis.
- Leia as instruções do repositório e preserve marca, linguagem, decisões de produto e arquitetura. Uma auditoria solicitada sem pedido de correção é somente leitura.
- Separe o site público das áreas autenticadas: uma página de login ou cadastro pode ter `noindex` intencional; não trate a nota de SEO dessa página como falha isolada.

## Conceber e desenvolver

- Defina a hierarquia da página a partir das perguntas de quem visita: o que é, para quem serve, como funciona, por que confiar e qual é o próximo passo. Escreva textos específicos e verificáveis antes de otimizar palavras-chave.
- Reaproveite a identidade e os componentes do projeto. Ao criar uma linguagem visual nova, estabeleça tipografia, cores, espaçamentos, estados interativos e comportamento responsivo; confira a página em telas reais ou em larguras representativas antes de multiplicar componentes.
- Construa com HTML semântico, mídia dimensionada, carregamento adequado ao que aparece primeiro, controles operáveis por teclado, foco visível e suporte a movimento reduzido quando houver animação. Vídeo deve ter caminho claro para reproduzir, pausar e compreender seu conteúdo.
- Faça formulários e CTAs conduzir a uma próxima etapa real, com mensagens claras de erro e sucesso. Não prometa downloads, integrações ou planos que ainda não estejam disponíveis.

## Examinar e melhorar

- Percorra a jornada no desktop e em larguras móveis representativas, inclusive telas estreitas (por exemplo, 320 e 390 px). Verifique navegação, aviso de consentimento, vídeo, formulários, estados vazios, erros e o próximo passo após cada CTA. Teste teclado e foco quando houver interação.
- Para sites com sitemap, rode o `scripts/audit_public_site.py` desta skill com a URL base, por exemplo `python3 /caminho/da/skill/scripts/audit_public_site.py https://dominio.example`. Ele verifica respostas, canônicas, títulos, descrições, H1 e texto alternativo. Confirme manualmente os achados e os links de maior valor.
- Meça páginas representativas com Lighthouse em celular e PC. Repita resultados anômalos antes de atribuí-los ao site; registre páginas, ambiente e variação. Diferencie métricas de laboratório de Core Web Vitals de usuários reais. Uma nota 100 de acessibilidade não substitui inspeção manual ou WCAG.
- Confira que SEO e GEO partem de conteúdo específico e verificável, páginas rastreáveis, links claros e metadados corretos. Use Search Console quando disponível para verificar indexação; sitemap e nota SEO 100 não a garantem. Confirme recomendações atuais nas fontes oficiais antes de sugerir recursos especiais para IA.
- Se houver Analytics, compare ID do código com o fluxo correto, consentimento antes da coleta opcional, proteção contra dados pessoais, recebimento de eventos e significado das conversões. Não trate `purchase` de contratação como receita paga sem conciliação. Não gere cadastros, pagamentos ou conversões artificiais em produção só para obter um evento.
- Se o site distribuir software, confira disponibilidade, origem, assinatura do artefato final e instruções de instalação. Não normalize a passagem por avisos de segurança. Revise também cabeçalhos e atributos de cookies relevantes ao ambiente publicado.

## Implementar e concluir

- Quando o usuário pedir correções, priorize problemas reproduzíveis que afetem confiança, segurança, acesso e conclusão da jornada. Preserve o conteúdo e o visual aprovado, salvo pedido contrário.
- Valide no código, no build e na versão publicada conforme o escopo autorizado. Commit, push, publicação, mudanças em Analytics/Search Console e outras ações externas exigem autorização na conversa; um roteiro do repositório não a concede sozinho.
- Ao dar uma nota, exponha o que foi testado, problemas por prioridade e limites do teste. Dê uma avaliação própria da experiência e prontidão do site, separada das notas automáticas. Não atribua causalidade a uma mudança sem medição comparável anterior.

Leia [o caso Combinado em Família](references/caso-combinado.md) quando precisar de um exemplo concreto das falhas que passaram por uma auditoria automática com nota 100. Revalide qualquer fato do caso antes de aplicá-lo ao site atual.
