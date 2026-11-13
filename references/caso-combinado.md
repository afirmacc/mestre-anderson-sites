# Caso: Combinado em Família, novembro de 2026

Este caso preserva lições, não requisitos para outros sites. O estado de produção pode ter mudado; confira novamente antes de citar fatos ou tomar decisões.

## O que funcionou

- Produto e linguagem definidos antes do visual: combinados de tempo de tela, transparência para crianças e adolescentes, sem pressupor que quem cuida sejam pai e mãe.
- Identidade consistente (azul, preto, branco e amarelo), vídeo no topo móvel, páginas internas alinhadas à home e Ajuda com respostas específicas.
- Sitemap com 69 URLs públicas; todas responderam 200 e tinham título, descrição, H1 e canônica próprios na auditoria. Home, Ajuda e Baixar chegaram a 100 em Lighthouse móvel; a home também chegou a 100 no desktop.
- Uma execução da home marcou 69 em desempenho por tarefas longas não atribuídas. Duas repetições deram 100. A lição é relatar variação e investigar antes de transformar um número isolado em diagnóstico.

## O que a nota 100 não mostrou

- Em 320–390 px, parte da navegação horizontal e o acesso a “Entrar” ficavam escondidos sem sinal claro de rolagem. O aviso de estatísticas cobria conteúdo e ações na primeira visita.
- O cadastro marcou 96 em acessibilidade: um link ativo tinha contraste de 4,34:1, abaixo de 4,5:1 para aquele texto. Seu SEO 66 resultava de `noindex` intencional.
- O instalador Windows publicado não tinha assinatura Authenticode embutida. A página orientava a passar pelo aviso do SmartScreen. Isso afetava confiança e distribuição mais do que a pontuação Lighthouse.
- O cookie antifraude publicado não tinha atributo `Secure`, embora tivesse `HttpOnly` e `SameSite=Strict`.
- O fluxo web do GA4 recebia eventos e os eventos principais `sign_up` e `purchase` estavam configurados, mas não havia observação de ambos nos 28 dias verificados. `purchase` representava contratação, não mensalidade paga.
- O site informava que os apps Android estavam em análise na loja. Assim, uma jornada completa de uma nova família ainda dependia de disponibilidade externa.
- Search Console e métricas reais de usuários não foram verificados. Um sitemap válido não prova indexação.

## Autoria e causalidade

O histórico do repositório registra a base do site e a identidade visual com participação do Claude, trabalho posterior da Ajuda pelo Codex e ajustes de páginas, SEO e Analytics pelo Codex. O relatório com quatro notas 100 foi feito após esses ajustes. Não existe uma medição comparável anterior que permita atribuir a nota a um único agente.

Fontes de referência a conferir no momento de uso: [Google Search para recursos de IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), [Core Web Vitals](https://web.dev/articles/vitals), [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [SmartScreen e assinatura](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation) e [cookies antifraude no ASP.NET Core](https://learn.microsoft.com/aspnet/core/security/anti-request-forgery).
