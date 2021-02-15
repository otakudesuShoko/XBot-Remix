# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.

from asyncio import sleep
from os import remove

from telethon.errors import (
    BadRequestError,
    ChatAdminRequiredError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
    UserAdminInvalidError,
)
from telethon.errors.rpcerrorlist import MessageTooLongError, UserIdInvalidError
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    ChatAdminRights,
    ChatBannedRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
    PeerChat,
)

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register

# =================== CONSTANT ===================
PP_TOO_SMOL = "`The image is too small`"
PP_ERROR = "`Failure while processing the image`"
NO_ADMIN = "`I am not an admin!`"
NO_PERM = "`I don't have sufficient permissions!`"
NO_SQL = "`Running on Non-SQL mode!`"

CHAT_PP_CHANGED = "`Chat Picture Changed`"
CHAT_PP_ERROR = (
    "`Some issue with updating the pic,`"
    "`maybe coz I'm not an admin,`"
    "`or don't have enough rights.`"
)
INVALID_MEDIA = "`Invalid Extension`"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
# ================================================


@register(outgoing=True, pattern=r"^\.setgpic$")
async def set_group_photo(gpic):
    if not gpic.is_group:
        await gpic.edit("`Saya tidak berpikir ini adalah grup.`")
        return
    replymsg = await gpic.get_reply_message()
    chat = await gpic.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    photo = None

    if not admin and not creator:
        return await gpic.edit(NO_ADMIN)

    if replymsg and replymsg.media:
        await gpic.edit("`Mengganti poto Obrolan`")
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await gpic.client.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split("/"):
            photo = await gpic.client.download_file(replymsg.media.document)
        else:
            await gpic.edit(INVALID_MEDIA)

    if photo:
        try:
            await gpic.client(
                EditPhotoRequest(gpic.chat_id, await gpic.client.upload_file(photo))
            )
            await gpic.edit(CHAT_PP_CHANGED)

        except PhotoCropSizeSmallError:
            await gpic.edit(PP_TOO_SMOL)
        except ImageProcessFailedError:
            await gpic.edit(PP_ERROR)


@register(outgoing=True, pattern=r"^\.promote(?: |$)(.*)")
async def promote(promt):
    # Get targeted chat
    chat = await promt.get_chat()
    # Grab admin status or creator in a chat
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, also return
    if not admin and not creator:
        return await promt.edit(NO_ADMIN)

    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )

    await promt.edit("`Promot anak dajjal...`")
    user, rank = await get_user_from_event(promt)
    if not rank:
        rank = "Anak Dajjal"  # Just in case.
    if not user:
        return

    # Try to promote if current user is admin or creator
    try:
        await promt.client(EditAdminRequest(promt.chat_id, user.id, new_rights, rank))
        await promt.edit("`Mempromosikan anak dajjal sukses !`")
        await sleep(5)
        await promt.delete()

    # If Telethon spit BadRequestError, assume
    # we don't have Promote permission
    except BadRequestError:
        return await promt.edit(NO_PERM)

    # Announce to the logging group if we have promoted successfully
    if BOTLOG:
        await promt.client.send_message(
            BOTLOG_CHATID,
            "#PROMOTE ADMIN\n"
            f"Nama  : [{user.first_name}](tg://user?id={user.id})\n"
            f"GROUP : {promt.chat.title}(`{promt.chat_id}`)",
        )


@register(outgoing=True, pattern=r"^\.demote(?: |$)(.*)")
async def demote(dmod):
    # Admin right check
    chat = await dmod.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        return await dmod.edit(NO_ADMIN)

    # If passing, declare that we're going to demote
    await dmod.edit("`Pecat sebagai admin...`")
    rank = "Anak Dajjal"  # dummy rank, lol.
    user = await get_user_from_event(dmod)
    user = user[0]
    if not user:
        return

    # New rights after demotion
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    # Edit Admin Permission
    try:
        await dmod.client(EditAdminRequest(dmod.chat_id, user.id, newrights, rank))

    # If we catch BadRequestError from Telethon
    # Assume we don't have permission to demote
    except BadRequestError:
        return await dmod.edit(NO_PERM)
    await dmod.edit("`Pecat anak dajjal berhasil!`")
    await sleep(5)
    await dmod.delete()

    # Announce to the logging group if we have demoted successfully
    if BOTLOG:
        await dmod.client.send_message(
            BOTLOG_CHATID,
            "#PECAT ADMIN\n"
            f"NAMA   : [{user.first_name}](tg://user?id={user.id})\n"
            f"GROUP  : {dmod.chat.title}(`{dmod.chat_id}`)",
        )


@register(outgoing=True, pattern=r"^\.ban(?: |$)(.*)")
async def ban(bon):
    # Here laying the sanity check
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        return await bon.edit(NO_ADMIN)

    user, reason = await get_user_from_event(bon)
    if not user:
        return

    # Announce that we're going to whack the pest
    await bon.edit("`Sampah Masyarakat!`")

    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await bon.edit(NO_PERM)
    # Helps ban group join spammers more easily
    try:
        reply = await bon.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await bon.edit(
            "`Gua ga memiliki hak pesan ! Tapi tetap ae Lu dibanned!`"
        )
    # Delete message and then tell that the command
    # is done gracefully
    # Shout out the ID, so that fedadmins can fban later
    if reason:
        await bon.edit(
            f"`**🗑Jenis Sampah**:` [{user.first_name}](tg://user?id={user.id})\n`**ID**:` `{str(user.id)}` Dibanned !!\n`**Alasan**:` {reason}"
        )
    else:
        await bon.edit(
            f"`USER:` [{user.first_name}](tg://user?id={user.id})\n`ID:` `{str(user.id)}` was banned !!"
        )
    # Announce to the logging group if we have banned the person
    # successfully!
    if BOTLOG:
        await bon.client.send_message(
            BOTLOG_CHATID,
            "#BAN\n"
            f"NAMA   : [{user.first_name}](tg://user?id={user.id})\n"
            f"GROUP  : {bon.chat.title}(`{bon.chat_id}`)",
        )


@register(outgoing=True, pattern=r"^\.unban(?: |$)(.*)")
async def nothanos(unbon):
    # Here laying the sanity check
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        return await unbon.edit(NO_ADMIN)

    # If everything goes well...
    await unbon.edit("`Daur ulang sampah...`")

    user = await get_user_from_event(unbon)
    user = user[0]
    if not user:
        return

    try:
        await unbon.client(EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await unbon.edit("```Daur Ulang Sampah sukses```")
        await sleep(3)
        await unbon.delete()

        if BOTLOG:
            await unbon.client.send_message(
                BOTLOG_CHATID,
                "#UNBAN\n"
                f"NAMA  : [{user.first_name}](tg://user?id={user.id})\n"
                f"GROUP : {unbon.chat.title}(`{unbon.chat_id}`)",
            )
    except UserIdInvalidError:
        await unbon.edit("`Anak dajjal gagal dibanned!`")


@register(outgoing=True, pattern=r"^\.mute(?: |$)(.*)")
async def spider(spdr):
    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.spam_mute_sql import mute
    except AttributeError:
        return await spdr.edit(NO_SQL)

    # Admin or creator check
    chat = await spdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await spdr.edit(NO_ADMIN)

    user, reason = await get_user_from_event(spdr)
    if not user:
        return

    self_user = await spdr.client.get_me()

    if user.id == self_user.id:
        return await spdr.edit(
            "`Tidak bisa membisukan diri sendiri...\n(ヘ･_･)ヘ┳━┳`"
        )

    # If everything goes well, do announcing and mute
    await spdr.edit("`Mendapat rekaman!`")
    if mute(spdr.chat_id, user.id) is False:
        return await spdr.edit("`Gagal user telah dibisukan sebelumnya`")
    else:
        try:
            await spdr.client(EditBannedRequest(spdr.chat_id, user.id, MUTE_RIGHTS))

            # Announce that the function is done
            if reason:
                await spdr.edit(f"`🔇**DIBISUKAN** !!`\n**ALASAN**: {reason}")
            else:
                await spdr.edit("`Safely taped !!`")

            # Announce to logging group
            if BOTLOG:
                await spdr.client.send_message(
                    BOTLOG_CHATID,
                    "#MEMBISUKAN\n"
                    f"NAMA   : [{user.first_name}](tg://user?id={user.id})\n"
                    f"GROUP  : {spdr.chat.title}(`{spdr.chat_id}`)",
                )
        except UserIdInvalidError:
            return await spdr.edit("`Oh mute gagal asw!`")


@register(outgoing=True, pattern=r"^\.unmute(?: |$)(.*)")
async def unmoot(unmot):
    # Admin or creator check
    chat = await unmot.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await unmot.edit(NO_ADMIN)

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.spam_mute_sql import unmute
    except AttributeError:
        return await unmot.edit(NO_SQL)

    # If admin or creator, inform the user and start unmuting
    await unmot.edit("```Membuka akses pesan...```")
    user = await get_user_from_event(unmot)
    user = user[0]
    if not user:
        return

    if unmute(unmot.chat_id, user.id) is False:
        return await unmot.edit("`Gagal! User sudah tidak dibisukan.`")
    else:

        try:
            await unmot.client(EditBannedRequest(unmot.chat_id, user.id, UNBAN_RIGHTS))
            await unmot.edit("```Membuka askses chat sukses```")
            await sleep(3)
            await unmot.delete()
        except UserIdInvalidError:
            return await unmot.edit("`Asw telah terjadj kesalahan!`")

        if BOTLOG:
            await unmot.client.send_message(
                BOTLOG_CHATID,
                "#UNMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {unmot.chat.title}(`{unmot.chat_id}`)",
            )


@register(incoming=True)
async def muter(moot):
    try:
        from userbot.modules.sql_helper.gmute_sql import is_gmuted
        from userbot.modules.sql_helper.spam_mute_sql import is_muted
    except AttributeError:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                await moot.delete()
                await moot.client(
                    EditBannedRequest(moot.chat_id, moot.sender_id, rights)
                )
    for i in gmuted:
        if i.sender == str(moot.sender_id):
            await moot.delete()


@register(outgoing=True, pattern=r"^\.ungmute(?: |$)(.*)")
async def ungmoot(un_gmute):
    # Admin or creator check
    chat = await un_gmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await un_gmute.edit(NO_ADMIN)

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import ungmute
    except AttributeError:
        return await un_gmute.edit(NO_SQL)

    user = await get_user_from_event(un_gmute)
    user = user[0]
    if not user:
        return

    # If pass, inform and start ungmuting
    await un_gmute.edit("```Membuka akses pesan...```")

    if ungmute(user.id) is False:
        await un_gmute.edit("`Gagal! Anak dajjal sudah bebaz.`")
    else:
        # Inform about success
        await un_gmute.edit("```Membuka akses pesan sukses```")
        await sleep(3)
        await un_gmute.delete()

        if BOTLOG:
            await un_gmute.client.send_message(
                BOTLOG_CHATID,
                "#UNGMUTE\n"
                f"NAMA   : [{user.first_name}](tg://user?id={user.id})\n"
                f"GROUP  : {un_gmute.chat.title}(`{un_gmute.chat_id}`)",
            )


@register(outgoing=True, pattern=r"^\.gmute(?: |$)(.*)")
async def gspider(gspdr):
    # Admin or creator check
    chat = await gspdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await gspdr.edit(NO_ADMIN)

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import gmute
    except AttributeError:
        return await gspdr.edit(NO_SQL)

    user, reason = await get_user_from_event(gspdr)
    if not user:
        return

    # If pass, inform and start gmuting
    await gspdr.edit("`Mampus! Bisukan anak dajjal secara global`")
    if gmute(user.id) is False:
        await gspdr.edit("`Gagal! User sudah dibisukam global.\nCoba dilain hari.`")
    else:
        if reason:
            await gspdr.edit(f"`🔇MUTE GLOBAL!`\n**ALASAN**: {reason}")
        else:
            await gspdr.edit("`Dibisukan secara global!`")

        if BOTLOG:
            await gspdr.client.send_message(
                BOTLOG_CHATID,
                "#GMUTE\n"
                f"NAMA  : [{user.first_name}](tg://user?id={user.id})\n"
                f"GROUP : {gspdr.chat.title}(`{gspdr.chat_id}`)",
            )


@register(outgoing=True, pattern=r"^\.zombies(?: |$)(.*)", groups_only=False)
async def rm_deletedacc(show):

    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "`Tidak ada akun terhapus, group anda beraih`"

    if con != "clean":
        await show.edit("`Mencari akun setan di obrolan ...`")
        async for user in show.client.iter_participants(show.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = (
                f"`Menemukan` **{del_u}** `Akun setan di group ini,"
                "\nGroup ini harus diruqyah`")
        return await show.edit(del_status)

    # Here laying the sanity check
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        return await show.edit("`Anda bukan admin di group ini!`")

    await show.edit("`❗ Menghapus akun setan...\nOh gua lakukan itu?!?!`")
    del_u = 0
    del_a = 0

    async for user in show.client.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                return await show.edit("`Saya tidak memiliki hak untuk ban`")
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await show.client(EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"Membersihkan **{del_u}** Hapus akun"

    if del_a > 0:
        del_status = (
            f"Membersihkan **{del_u}** Menghapus akun"
            f"\n**{del_a}** Akun tidak dapat dihapus"
        )
    await show.edit(del_status)
    await sleep(2)
    await show.delete()

    if BOTLOG:
        await show.client.send_message(
            BOTLOG_CHATID,
            "#CLEANUP\n"
            f"Cleaned **{del_u}** Menghapus akun !!"
            f"\nCHAT: {show.chat.title}(`{show.chat_id}`)",
        )


@register(outgoing=True, pattern=r"^\.admins$")
async def get_admin(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = f"<b>Daftar Admin  {title}:</b> \n"
    try:
        async for user in show.client.iter_participants(
            show.chat_id, filter=ChannelParticipantsAdmins
        ):
            if not user.deleted:
                link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                mentions += f"\n{link}"
            else:
                mentions += f"\nMenghapus akun <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    await show.edit(mentions, parse_mode="html")


@register(outgoing=True, pattern=r"^\.pin(?: |$)(.*)")
async def pin(msg):
    # Admin or creator check
    chat = await msg.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await msg.edit(NO_ADMIN)

    to_pin = msg.reply_to_msg_id

    if not to_pin:
        return await msg.edit("`Balas ke pesan untuk sematkan pesan.`")

    options = msg.pattern_match.group(1)

    is_silent = True

    if options.lower() == "loud":
        is_silent = False

    try:
        await msg.client(UpdatePinnedMessageRequest(msg.to_id, to_pin, is_silent))
    except BadRequestError:
        return await msg.edit(NO_PERM)

    await msg.edit("`Sematkan pesan sukses!`")
    await sleep(2)
    await msg.delete()

    user = await get_user_from_id(msg.from_id, msg)

    if BOTLOG:
        await msg.client.send_message(
            BOTLOG_CHATID,
            "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {msg.chat.title}(`{msg.chat_id}`)\n"
            f"LOUD: {not is_silent}",
        )


@register(outgoing=True, pattern=r"^\.kick(?: |$)(.*)")
async def kick(usr):
    # Admin or creator check
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        return await usr.edit(NO_ADMIN)

    user, reason = await get_user_from_event(usr)
    if not user:
        return await usr.edit("`Couldn't fetch user.`")

    await usr.edit("`Menendang dajjal...`")

    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(0.5)
    except Exception as e:
        return await usr.edit(NO_PERM + f"\n{str(e)}")

    if reason:
        await usr.edit(
            f"`Menendang` [{user.first_name}](tg://user?id={user.id})`!`\nKarena: {reason}"
        )
    else:
        await usr.edit(f"`Menendang` [{user.first_name}](tg://user?id={user.id})`!`")
        await sleep(5)
        await usr.delete()

    if BOTLOG:
        await usr.client.send_message(
            BOTLOG_CHATID,
            "#KICK\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {usr.chat.title}(`{usr.chat_id}`)\n",
        )


@register(outgoing=True, pattern=r"^\.users ?(.*)")
async def get_users(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "Users in {}: \n".format(title)
    try:
        if not show.pattern_match.group(1):
            async for user in show.client.iter_participants(show.chat_id):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
                else:
                    mentions += f"\nDeleted Account `{user.id}`"
        else:
            searchq = show.pattern_match.group(1)
            async for user in show.client.iter_participants(
                show.chat_id, search=f"{searchq}"
            ):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
                else:
                    mentions += f"\nMenghapus Akun `{user.id}`"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit("Sial, ini grup yang sangat besar. Mengupload daftar pengguna sebagai file.")
        file = open("userslist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "userslist.txt",
            caption="Users in {}".format(title),
            reply_to=show.id,
        )
        remove("userslist.txt")


async def get_user_from_event(event):
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id and len(args) != 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            return await event.edit("`Balas dengan menyertai username atau balas pesan pengguna!`")

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(
                    probable_user_mention_entity,
                    MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            return await event.edit(str(err))

    return user_obj, extra


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        return await event.edit(str(err))

    return user_obj


@register(outgoing=True, pattern=r"^\.usersdel ?(.*)")
async def get_usersdel(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "Menghapus pengguna in {}: \n".format(title)
    try:
        if not show.pattern_match.group(1):
            async for user in show.client.iter_participants(show.chat_id):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
        #       else:
        #                mentions += f"\nDeleted Account `{user.id}`"
        else:
            searchq = show.pattern_match.group(1)
            async for user in show.client.iter_participants(
                show.chat_id, search=f"{searchq}"
            ):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
        #       else:
    #              mentions += f"\nDeleted Account `{user.id}`"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit(
            "Sial, ini grup yang sangat besar. Mengupload daftar pengguna yang dihapus sebagai file."
        )
        file = open("userslist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "deleteduserslist.txt",
            caption="Users in {}".format(title),
            reply_to=show.id,
        )
        remove("deleteduserslist.txt")


async def get_userdel_from_event(event):
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id and len(args) != 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            return await event.edit("`beri username pengguna untuk menghapus atau reply pesan!`")

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(
                    probable_user_mention_entity,
                    MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            return await event.edit(str(err))

    return user_obj, extra


async def get_userdel_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        return await event.edit(str(err))

    return user_obj


@register(outgoing=True, pattern=r"^\.bots$", groups_only=True)
async def get_bots(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = f"<b>Bots in {title}:</b>\n"
    try:
        if isinstance(show.to_id, PeerChat):
            return await show.edit("`I heard that only Supergroups can have bots.`")
        else:
            async for user in show.client.iter_participants(
                show.chat_id, filter=ChannelParticipantsBots
            ):
                if not user.deleted:
                    link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                    userid = f"<code>{user.id}</code>"
                    mentions += f"\n{link} {userid}"
                else:
                    mentions += f"\nDeleted Bot <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions, parse_mode="html")
    except MessageTooLongError:
        await show.edit("Damn, too many bots here. Uploading bots list as file.")
        file = open("botlist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "botlist.txt",
            caption="Bots in {}".format(title),
            reply_to=show.id,
        )
        remove("botlist.txt")


CMD_HELP.update(
    {
        "admin": "⎙__** MODULE NAME :** Admin__"
        "\n\n❏ **CMD** ➜ `.promote` (username/reply) (nama gelar)"
        "\n┗ **USAGE** ➜ Memberikan hak admin kepada orang dalam obrolan."
        "\n\n❏ **CMD** ➜ `.demote` (username/reply)"
        "\n┗ **USAGE** ➜ Mencabut izin admin seseorang dalam obrolan."
        "\n\n❏ **CMD** ➜ `.ban` (username/reply) (sebutkan alasannya)"
        "\n┗ **USAGE** ➜ Blokir seseorang di dalam obrolan."
        "\n\n❏ **CMD** ➜  `.unban` (username/reply)"
        "\n┗ **USAGE** ➜ Membuka blokir seseorang di dalam obrolan."
        "\n\n❏ **CMD** ➜ `.mute` (username/reply) (alasan membisukan)"
        "\n┗ **USAGE** ➜ Membisukan seseorang di dalam obrolan"
        "\n\n❏ **CMD** ➜ `.unmute` (username/reply)"
        "\n┗ **USAGE** ➜ Menghapus seseorang dari dalam daftar bisu."
        "\n\n❏ **CMD** ➜ `.gmute` (username/reply) (Alasan)"
        "\n┗ **USAGE** ➜ Bisukan orang tersebut di semua grup yang Anda sama dengan mereka."
        "\n\n❏ **CMD** ➜ `.ungmute` (username/reply)"
        "\n┗ **USAGE** ➜ Menghapus seseorang dari dalam daftar bisu."
        "\n\n❏ **CMD** ➜ `.zombies`"
        "\n┗ **USAGE** ➜ Mencari akun terhapus di dalam obrolan "
        "\nGunakan `.zombies clean` untuk menghapus akun yang dihapus dari grup"
        "\n\n❏ **CMD** ➜ `.all`"
        "\n┗ **USAGE** ➜ Tandai semua anggota di obrolan grup."
        "\n\n❏ **CMD** ➜ `.admins`"
        "\n┗ **USAGE** ➜ Mengambil daftar admin di obrolan."
        "\n\n❏ **CMD** ➜ `.bots`"
        "\n┗ **USAGE** ➜ Mengambil daftar bot di obrolan."
        "\n\n❏ **CMD** ➜ `.users` atau `.users` (Nama Member)"
        "\n┗ **USAGE** ➜ Melihat daftar pengguna atau melihat info pengguna."
        "\n\n❏ **CMD** ➜ `.setgpic` (reply ke gambar)"
        "\n┗ **USAGE** ➜ Mengganti profil di dalam obrolan"})
