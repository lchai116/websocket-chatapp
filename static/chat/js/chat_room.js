        var cur_channel = ''


        var chatItemTemplate = function(chat){
        var username = chat.username
        var content = chat.content
        var time = chat.creattime
        var avatar = chat.avatar
        var t = `
            <div class="oc-chat-item">
                <div class="oc-chatitem-container">
                    <div class="oc-chatitem-date"></div>
                    <a class="oc-chatitem-avatar" href="#">
                        <img class="oc-avatar" src="${avatar}" height="36" width="36">
                    </a>
                    <div class="oc-chatitem-cell">
                        <div class="oc-chatitem-info">
                            <strong><a href="#">${username}</a></strong>
                            &nbsp;  •  &nbsp;
                            &nbsp<time class="oc-time-stamp" data-time="${time}"></time>
                        </div>
                        <div class="oc-chatitem-content">${content}</div>
                    </div>
                </div>
            </div>
            `
            return t
        }

        var userListItemTemplate = function(userItem){
            var username = userItem.username
            var avatar = userItem.avatar
            var u = `
                <div class="user-item">
                    <a class="oc-userlist-avatar" href="#">
                        <img class="oc-avatar" src="${avatar}" height="25" width="25">
                    </a>
                    <div class="user-item-name">
                        &nbsp;    &nbsp;
                        <span><a href="#">${username}</a></span>
                    </div>
                </div>
                `
            return u
        }


        var scrollToBottom = function(){
            var height = $(document).height()
            $('body').animate({
                scrollTop: height
            }, 300)
        }


        var insertChatItem = function(chat){
            var selector = '#id-div-chats'
            var chatsDiv = $(selector)
            var t = chatItemTemplate(chat)
            chatsDiv.append(t)
            longTimeAgo()
            scrollToBottom()
        }


        var chatResponse = function(r){
            //var chat = JSON.parse(r)
            var chat = r
            if(cur_channel == chat.cur_channel){
                insertChatItem(chat)
            }
        }


		var safeStr = function(str){
			return str.replace(/</g,'&lt;').replace(/>/g,'&gt;')
		}


        var socket
        var socketInit = function(){
            socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/chat/lobby')
            socket.on('connect', function(){
                //socket.emit('joined', {cur_channel: cur_channel})
            })

            socket.on('myresp', function(data){
                chatResponse(data)
            })

            socket.on('member update', function(data){
                insertUserItems(data)
            })
        }


        var insertChannelMsgs = function(srv_rsp){
            var channelMsgs = srv_rsp.data.msgs_in_room
            var selector = '#id-div-chats'
            var chatsDiv = $(selector)
            var html = channelMsgs.map(chatItemTemplate)
            chatsDiv.empty()
            chatsDiv.append(html.join(''))
            longTimeAgo()
            scrollToBottom()
        }


        var insertUserItems = function(data){
            var userItems = data.member_in_room
            var selector = '.user-list'
            var userItemsDiv = $(selector)
            var html = userItems.map(userListItemTemplate)
            userItemsDiv.empty()
            userItemsDiv.append(html.join(''))
            $('#user-counter').text(userItems.length)
            //scrollToBottom()
        }


        var channelInit = function(srv_rsp){
            if(srv_rsp.success){
                $('#id-roomname').text(cur_channel)
                insertChannelMsgs(srv_rsp)
            } else{
                alert(srv_rsp.message)
            }
        }


        var bindEventChannelSelect = function(){
            $('.side-channel-item').on('click', function(event){
                event.preventDefault()
                var self = $(this)
                cur_channel = self.text()
                $('.side-channel-item').removeClass('side-channel-active')
                self.addClass('side-channel-active')
                socket.emit('joined', {cur_channel: cur_channel})
                api.post('/chat/channelMsg', {cur_channel: cur_channel}, channelInit)
                log('btn click: and join sent', cur_channel)
            })
        }


        var bindEventMsgSend = function(){
            $('#id-button-send').on('click', function(){
                //var username = $('#id-input-name').val()
                var content = $('#id-input-content').val()
				log(safeStr(content))
                if(content != ""){
                    var data = {
                        content: safeStr(content),
                        cur_channel: cur_channel,
                    }
                    socket.emit('chat', data)
                }
            })
        }


        var bindEventEnterKeypress = function(){
            $('#id-input-content').keypress(function(event){
                var code = event.keyCode || event.which
                if(code == 13){
                    $('#id-button-send').click()
                    setTimeout(function(){
                        $('#id-input-content').val('')
                    }, 80)
                    //$('#id-input-content').val('')
                }
            })
        }


        var bindEventWindowClose = function(){
            $(window).bind('beforeunload',function(){
                socket.emit('close broadcast', {cur_channel: cur_channel})
                socket.close()
            });
        }


        var __main = function(){
            socketInit()
            bindEventChannelSelect()
            bindEventEnterKeypress()
            bindEventMsgSend()
            bindEventWindowClose()
            $('.side-channel-item')[0].click()
        }


        $(document).ready(function(){
            __main()
        })
