        var cur_channel = ''
        var log = function(){
            console.log(arguments)
        }

        var api = {}
        api.ajax = function(url, method, form, callback){
            request = {
                url: url,
                type: method,
                data: form,
                success: function(response){
                    log('success')
                    r = JSON.parse(response)
                    callback(r)
                },
                error: function(err){
                    r = {
                        success: false,
                        message: 'error',
                    }
                    callback(r)
                },
            }
            $.ajax(request)
        }

        api.post = function(url, form, response){
            api.ajax(url, 'post', form, response)
        }


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

        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/chat/lobby')
        var socketInit = function(){
            socket.on('connect', function(){
                //socket.emit('joined', {cur_channel: cur_channel})
            })
            socket.on('counter', function(data){

            })

            $('#id-button-send').on('click', function(){
                //var username = $('#id-input-name').val()
                var content = $('#id-input-content').val()
				log(safeStr(content))
                if(content != ""){
                    var data = {
                        //username: username,
                        content: safeStr(content),
                        cur_channel: cur_channel,
                    }
                    socket.emit('chat', data)
                }

            })

            socket.on('myresp', function(data){
                chatResponse(data)
            })

            socket.on('stat-tst', function(data){
                log(data)
            })

            socket.on('member update', function(data){
                inserUserItems(data)
            })

            return socket
        }

        var inserChannelMsgs = function(srv_rsp){
            var channelMsgs = srv_rsp.data.msgs_in_room
            var selector = '#id-div-chats'
            var chatsDiv = $(selector)
            var html = channelMsgs.map(chatItemTemplate)
            chatsDiv.empty()
            chatsDiv.append(html.join(''))
            longTimeAgo()
            scrollToBottom()
        }

        var inserUserItems = function(data){
            log('user item')
            var userItems = data.member_in_room
            var selector = '.user-list'
            var userItemsDiv = $(selector)
            var html = userItems.map(userListItemTemplate)
            userItemsDiv.empty()
            userItemsDiv.append(html.join(''))
            log('user item ist', userItems.length)
            $('#user-counter').text(userItems.length)
            //scrollToBottom()
        }

        var channelInit = function(srv_rsp){
            if(srv_rsp.success){
                $('#id-roomname').text(cur_channel)
             //   inserUserItems(srv_rsp)
                inserChannelMsgs(srv_rsp)

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
        
        // long time ago
        var longTimeAgo = function() {
            var timeAgo = function(time, ago) {
                return Math.round(time) + ago
            }
    
            $('time').each(function(i, e){
                var past = parseInt(e.dataset.time)
                var now = Math.round(new Date().getTime() / 1000)
                var seconds = now - past
                var ago = seconds / 60
                // log('time ago', e, past, now, ago)
                var oneHour = 60
                var oneDay = oneHour * 24
                // var oneWeek = oneDay * 7
                var oneMonth = oneDay * 30
                var oneYear = oneMonth * 12
                var s = ''
                if(seconds < 60) {
                    s = timeAgo(seconds, ' 秒前')
                } else if (ago < oneHour) {
                    s = timeAgo(ago, ' 分钟前')
                } else if (ago < oneDay) {
                    s = timeAgo(ago/oneHour, ' 小时前')
                } else if (ago < oneMonth) {
                    s = timeAgo(ago / oneDay, ' 天前')
                } else if (ago < oneYear) {
                    s = timeAgo(ago / oneMonth, ' 月前')
                }
                $(e).text(s)
            })
        }
        

        var __main = function(){
            var sock = socketInit()
            bindEventChannelSelect()
            bindEventEnterKeypress()
            bindEventWindowClose()
            $('.side-channel-item')[0].click()
        }

        $(document).ready(function(){
            __main()
        })