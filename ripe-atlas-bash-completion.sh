## This is highly inspired from Django's manage.py autocompletion
## https://github.com/django/django/blob/1.9.4/extras/django_bash_completion#L42-L57
## To install this, add the following line to your .bash_profile:
##
## . ~/path/to/django_bash_completion

_ripe_atlas_bash_completion()
{
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   RIPE_ATLAS_AUTO_COMPLETE=1 $1 ) )
}
complete -F _ripe_atlas_bash_completion -o default ripe-atlas
