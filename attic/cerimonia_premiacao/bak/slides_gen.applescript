#!/usr/bin/osascript

set kYear to "2018"
set kObiEdition to "XXI"
set kIcMembers to {{"Prof. Dr. Rodolfo Jardim de Azevedo", "Diretor do Instituto de Computação da Unicamp "}, {"Prof. Dr. Ricardo de Oliveira Anido", "Professor do Instituto de  Computação da Unicamp\n\nCoordenador da OBI" & kYear}}

on getTokens(txt, delimiter)
	set ans to {}
	set cur to ""
	repeat with c in txt
		if c as string = delimiter
			if length of cur is greater than 0 and not (cur = "HM")
				copy cur to the end of ans
			end if
			set cur to ""
		else
			set cur to cur & c
		end if
	end repeat
	if length of cur is greater than 0
		copy cur to the end of ans
	end if
	return ans
end getTokens

on getRevWinnersList(category)
	set ans to {}
	set foo to (open for access (POSIX file ("raw/" & category & ".txt")))
	set txt to paragraphs of (read foo for (get eof foo) as «class utf8»)
	set kMedals to {"OURO", "PRATA", "BRONZE", "HONRA AO MÉRITO"}
	set curMedalIdx to 0
	repeat with nextLine in txt
		if length of nextLine is greater than 0 then
			set tokens to {item (curMedalIdx+1) of kMedals} & getTokens(nextLine, "\t")
			set tokensProp to {medal:(item 1 of tokens), stageGroup:(item 2 of tokens), rank:(item 3 of tokens), name:(item 5 of tokens), school:(item 6 of tokens), city:(item 7 of tokens), state:(item 8 of tokens)}
			set ans to ans & {tokensProp}
		else
			set curMedalIdx to (curMedalIdx + 1) mod 4
		end if
	end repeat
	close access foo
	return reverse of ans
end getRevWinnersList

on getListFromFile(listName, maxPerString)
	set ans to {}
	set foo to (open for access (POSIX file ("raw/" & listName & ".txt")))
	set txt to paragraphs of (read foo for (get eof foo) as «class utf8»)
	set curCount to 0
	set cur to ""
	repeat with nextLine in txt
		if length of nextLine > 0
			if curCount = maxPerString
				set curCount to 0
				if length of cur > 0
					set ans to (ans & {cur})
					set cur to ""
				end if
			end if
			if length of cur > 0
				set cur to (cur & "\n\n")
			end if
			set cur to (cur & nextLine)
			set curCount to (curCount + 1)
		end if
	end repeat
	close access foo
	if length of cur > 0
		set ans to (ans & {cur})
	end if	
	return ans
end getListFromFile

on getWinnerDesc(info)
	set ans to (name of info)
	set ans to ans & ("\n" & (school of info) & " - " & (city of info) & "/" & (state of info))
	set ans to ans & ("\n(" & (rank of info) & "º Lugar)")
	return ans
end getWinnerDesc

on createTitleAndSubtitleSlide(thisDocument, title, subtitle, transition)
	tell application "Keynote"
		activate
		tell thisDocument
			set thisSlide to ¬
				make new slide with properties {base slide:master slide "Title & Subtitle"}
			tell thisSlide
				set the object text of the default title item to title
				set the object text of the default body item to subtitle
				if not transition = null
					set the transition properties to {transition effect:transition, transition duration:1.0, transition delay:0.0, automatic transition:false}			
				end if
				-- TODO
				-- set the height of the default title item to ((height of the thisDocument) * 0.45)
				-- set the height of the default body item to ((height of the thisDocument) * 0.45)
			end tell
		end tell
	end tell	
end createTitleAndSubtitleSlide

on numOccurences(textVal, charVal)
	set ans to 0
	repeat with c in textVal
		if (c as string) = charVal
			set ans to (ans + 1)
		end if
	end repeat
	return ans
end numOccurences

on createTitleAndBulletsSlide(thisDocument, title, body, winnersBody, transition, bodySize)
	tell application "Keynote"
		activate
		tell thisDocument
			set thisSlide to ¬
				make new slide with properties {base slide:master slide "Title - Top"}
			tell thisSlide
				set the object text of the default title item to title
				set bodyTextItem to ¬
					make new text item with properties {object text:body}
				if winnersBody = true
					set sizes to {44, 31}
					set szIdx to 1
					tell the default title item
						repeat with i from 1 to the length of title
							if i=1 or (not ((item i of title) as string = "\n") and ((item (i-1) of title) as string = "\n"))
								set szIdx to (szIdx+1) mod 2
							end if
							set the size of character i of object text to (item (szIdx+1) of sizes)
						end repeat
					end tell

					set sizes to {30, 21, 22}
					if my numOccurences(body, "\n") > 8 then set sizes to {17, 14, 15} -- TODO make this more generic

					set fontNames to {"Palatino", "Palatino Italic", "Palatino Italic"}
					set szIdx to 2
					tell bodyTextItem
						repeat with i from 1 to the length of body
							if i=1 or (not ((item i of body) as string = "\n") and ((item (i-1) of body) as string = "\n"))
								set szIdx to (szIdx+1) mod 3
							end if
							set the size of character i of object text to (item (szIdx+1) of sizes)
							set the font of character i of object text to (item (szIdx+1) of fontNames)
						end repeat
					end tell
				else
					set the size of the object text of the bodyTextItem to bodySize
				end if

				if not transition = null
					set the transition properties to {transition effect:transition, transition duration:1.0, transition delay:0.0, automatic transition:false}
				end if
			end tell
		end tell
	end tell	
end createTitleAndBulletsSlide

on createTitleCenterSlide(thisDocument, title, transition)
	tell application "Keynote"
		activate
		tell thisDocument
			set thisSlide to ¬
				make new slide with properties {base slide:master slide "Title - Center"}
			tell thisSlide
				set the object text of the default title item to title
				if not transition = null
					set the transition properties to {transition effect:transition, transition duration:1.0, transition delay:0.0, automatic transition:false}
				end if
			end tell
		end tell
	end tell	
end createTitleCenterSlide

on createBlankSlide(thisDocument)
	tell application "Keynote"
		activate
		tell thisDocument
			set thisSlide to ¬
				make new slide with properties {base slide:master slide "Blank"}
		end tell
	end tell	
end createBlankSlide

on createSlidesOfCategory(thisDocument, curCat, winnersList)
	tell application "Keynote"
		activate
		tell thisDocument
			set winnersCount to length of winnersList
			set idx to 1
			set curMedal to ""
			set curMedalLabel to ""
			set curCatLabel to "MODALIDADE " & curCat
			my createTitleCenterSlide(thisDocument, curCatLabel, swoosh)
			repeat while idx <= winnersCount
				set newMedal to (medal of (item idx of winnersList))
				if not newMedal = curMedal
					set curMedal to newMedal
					if curMedal = "HONRA AO MÉRITO"
						set curMedalLabel to curMedal
					else
						set curMedalLabel to "MEDALHA DE " & curMedal
					end if
					my createTitleAndSubtitleSlide(thisDocument, curMedalLabel, curCatLabel, cube)
				end if
				set title to (curMedalLabel & "\n" & curCatLabel)
				set curGroup to (stageGroup of ((item idx) of winnersList))
				set body to ""
				repeat while idx <= winnersCount and (stageGroup of ((item idx) of winnersList)) = curGroup
					if length of body > 0 then set body to (body & "\n\n\n")
					set body to (body & my getWinnerDesc(item idx of winnersList))
					set idx to idx+1
				end repeat
				my createTitleAndBulletsSlide(thisDocument, title, body, true, reveal, 0)
			end repeat
			my createBlankSlide(thisDocument)
		end tell
	end tell	
end createSlidesOfCategory

tell application "Keynote"
	activate
	set thisDocument to ¬
		make new document with properties {document theme:theme "awards_template.kth"}
	tell thisDocument
		-- cover
		set the base slide of the first slide to master slide "Title - Top"
		tell first slide
			set the object text of the default title item to "OBI" & kYear
			set bodyTextItem to ¬
				make new text item with properties {object text:kObiEdition & " Olimpíada Brasileira de Informática"}
			set the size of the object text of bodyTextItem to 50
			set the font of the object text of bodyTextItem to "Copperplate"
			set the color of the object text of bodyTextItem to "black"
			set the transition properties to {transition effect:doorway, transition duration:1.0, transition delay:0.0, automatic transition:false}			
		end tell

		-- ic members
		repeat with icMember in kIcMembers
			my createTitleAndSubtitleSlide(thisDocument, item 1 of icMember, item 2 of icMember, null)
		end repeat

		-- medals
		repeat with catEntry in {{"INICIAÇÃO NÍVEL 1", "ini1"}, {"INICIAÇÃO NÍVEL 2", "ini2"}, {"PROGRAMAÇÃO JÚNIOR", "pj"}, {"PROGRAMAÇÃO NÍVEL 1", "p1"}, {"PROGRAMAÇÃO NÍVEL 2", "p2"}}
		-- repeat with catEntry in {{"PROGRAMAÇÃO NÍVEL 2", "testp2"}}
			set cat to (item 1 of catEntry)
			set winnersList to my getRevWinnersList(item 2 of catEntry)
			my createSlidesOfCategory(thisDocument, cat, winnersList)
		end repeat

		--ioi
		my createTitleCenterSlide(thisDocument, "RESULTADOS DA SELETIVA IOI", cube)
		my createTitleAndBulletsSlide(thisDocument, "Classificados\nSeletiva IOI", item 1 of my getListFromFile("ioi", 4), false, reveal, 30)

		-- professors
		repeat with entry in my getListFromFile("professors", 5)
			my createTitleAndBulletsSlide(thisDocument, "Agradecimentos - Professores", entry, false, mosaic, 20)
		end repeat

		-- assistants
		repeat with entry in my getListFromFile("assistants", 6)
			my createTitleAndBulletsSlide(thisDocument, "Agradecimentos - Monitores", entry, false, reflection, 20)
		end repeat

		my createBlankSlide(thisDocument)
	end tell
end tell