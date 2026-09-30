#show: doc => cv(
$if(title)$  title: [$title$],$endif$
$if(cv-first-name)$  first-name: [$cv-first-name$],$endif$
$if(cv-last-name)$  last-name: [$cv-last-name$],$endif$
$if(cv-position)$  position: [$cv-position$],$endif$
$if(cv-affiliation)$  affiliation: [$cv-affiliation$],$endif$
$if(cv-contact-left)$  contact-left: ($for(cv-contact-left)$[$cv-contact-left$],$endfor$),$endif$
$if(cv-contact-right)$  contact-right: ($for(cv-contact-right)$[$cv-contact-right$],$endfor$),$endif$
$if(cv-date)$  date: [$cv-date$],$endif$
$if(cv-accent)$  accent: rgb("$cv-accent$"),$endif$
$if(cv-font)$  font: "$cv-font$",$endif$
$if(cv-fontsize)$  fontsize: $cv-fontsize$,$endif$
  doc,
)
