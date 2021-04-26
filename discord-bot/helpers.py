def user_parse(ctx):
    return ctx.author.id, ctx.author.display_name


help_message = """-
[GENERAL]
!help - shows this message
!passcode the_passcode - Activates the bot
!answer <prompt> - AI responds to your prompt
!complete <prompt> - AI completes your prompt
!emojify <prompt> - AI emojifies your prompt
!foulmouth <prompt> - AI responds with offensive language
!headline <prompt> - AI creates a news headline from your prompt
!sarcasm <prompt> - AI responds sarcastically
!sentiment <prompt> - AI rates your prompt (positive, neutral, negative)
!song <prompt> - AI creates a song with prompt as the song name

"""
