

on run argv

    set newTrackPath to posix file (item 1 of argv)
    --repeat with theItem in argv
    --    display dialog theItem as string
    --end repeat
    tell application "iTunes"
        activate
        set newTrack to add newTrackPath
       
        if item 2 of argv is equal to "TV show" then
            set video kind of newTrack to TV show
        else
            set video kind of newTrack to movie
        end if
        
        if item 3 of argv is not equal to "None" then
            set showName to item 3 of argv as string
            set show of newTrack to showName
        end if
        
        if item 4 of argv is not equal to "None" then
            set seasonNumber to item 4 of argv as integer
            set season number of newTrack to seasonNumber
        end if
        
        if item 5 of argv is not equal to "None" then
            set episodeNumber to item 5 of argv as integer
            set track number of newTrack to episodeNumber
            set episode number of newTrack to episodeNumber
        end if
        if item 6 of argv is not equal to "None" then
            tell newTrack
                try 
                    set desc to item 6 of argv as string
                    set long description to desc
                end try
            --set description of newTrack to desc
            end tell
        end if
        
        return 0
    end tell
end run
