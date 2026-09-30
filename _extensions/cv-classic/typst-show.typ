#show: doc => cv(
$if(title)$  title: [$title$],$endif$
$if(subtitle)$  subtitle: [$subtitle$],$endif$
$if(cv-contact-left)$  contact-left: ($for(cv-contact-left)$[$cv-contact-left$],$endfor$),$endif$
$if(cv-contact-right)$  contact-right: ($for(cv-contact-right)$[$cv-contact-right$],$endfor$),$endif$
$if(cv-date)$  date: [$cv-date$],$endif$
$if(cv-accent)$  accent: rgb("$cv-accent$"),$endif$
$if(cv-font)$  font: "$cv-font$",$endif$
$if(cv-fontsize)$  fontsize: $cv-fontsize$,$endif$
  doc,
)
