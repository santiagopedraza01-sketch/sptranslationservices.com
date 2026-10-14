<?xml version="1.0" encoding="UTF-8"?>
<!-- Renders sitemap.xml, page-sitemap.xml and post-sitemap.xml as a readable table in browsers.
     Search engines ignore this file. -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="robots" content="noindex,follow"/>
  <title>XML Sitemap — SP Translations</title>
  <style>
    body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;color:#444;background:#fff}
    #content{margin:0 auto;padding:30px 16px 60px;max-width:1100px}
    h1{color:#111D2C;font-size:2.2rem;margin:0 0 20px}
    p.expl{margin:14px 0;font-size:1.05rem}
    a{color:#000;text-decoration:none}
    p.expl a{color:#A8875A;font-weight:600}
    a:hover{text-decoration:underline}
    table{border:none;border-collapse:collapse;width:100%;margin-top:22px}
    th{text-align:left;padding:8px 5px;border-bottom:1px solid #111D2C;font-size:1rem}
    td{padding:6px 5px;font-size:.95rem;word-break:break-all}
    tr:nth-child(odd) td{background:#EEE}
    tbody tr:hover td{background:#CCC}
    td.n{width:90px;text-align:left;word-break:normal}
    td.d{width:200px;white-space:nowrap;word-break:normal}
    @media (max-width:640px){ td.n,th.n{display:none} td.d{width:auto;white-space:normal} }
  </style>
</head>
<body>
<div id="content">
  <h1>XML Sitemap</h1>
  <p class="expl">This is an XML Sitemap for <a href="https://sptranslationservices.com/">sptranslationservices.com</a>, meant for consumption by search engines.</p>
  <p class="expl">You can find more information about XML sitemaps on <a href="https://www.sitemaps.org/" rel="noopener" target="_blank">sitemaps.org</a>.</p>
  <xsl:if test="count(sitemap:sitemapindex/sitemap:sitemap) &gt; 0">
    <p class="expl">This XML Sitemap Index file contains <xsl:value-of select="count(sitemap:sitemapindex/sitemap:sitemap)"/> sitemaps.</p>
    <table>
      <thead><tr><th>Sitemap</th><th class="d">Last Modified</th></tr></thead>
      <tbody>
      <xsl:for-each select="sitemap:sitemapindex/sitemap:sitemap">
        <tr>
          <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
          <td class="d"><xsl:value-of select="concat(substring(sitemap:lastmod,1,10),' ',substring(sitemap:lastmod,12,5),' ',substring(sitemap:lastmod,20,6))"/></td>
        </tr>
      </xsl:for-each>
      </tbody>
    </table>
  </xsl:if>
  <xsl:if test="count(sitemap:sitemapindex/sitemap:sitemap) &lt; 1">
    <p class="expl">This XML Sitemap contains <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> URLs.</p>
    <p class="expl"><a href="/sitemap.xml">↑ Sitemap index</a></p>
    <table>
      <thead><tr><th>URL</th><th class="n">Images</th><th class="d">Last Mod.</th></tr></thead>
      <tbody>
      <xsl:for-each select="sitemap:urlset/sitemap:url">
        <tr>
          <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
          <td class="n"><xsl:value-of select="count(image:image)"/></td>
          <td class="d"><xsl:value-of select="concat(substring(sitemap:lastmod,1,10),' ',substring(sitemap:lastmod,12,5),' ',substring(sitemap:lastmod,20,6))"/></td>
        </tr>
      </xsl:for-each>
      </tbody>
    </table>
  </xsl:if>
</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
