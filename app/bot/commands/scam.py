import requests
import logging
from aiogram import types
from aiogram.filters import Command
from bot import dp
from app.database.crud import get_user_language

# Логирование
logging.basicConfig(level=logging.INFO)

@dp.message(Command(commands=['scam_token']))
async def scam_token_handler(message: types.Message):
    try:
        # Извлечение адреса токена из сообщения
        token_address = message.text.split()[1]

        # Получаем язык пользователя
        user_id = message.from_user.id
        language = get_user_language(user_id)

        # Выполняем GET запрос к Honeypot API
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',
            params={'address': token_address}
        )
        
        # Проверяем, если запрос выполнен успешно
        response.raise_for_status()

        data = response.json()

        # Определение ответов на двух языках
        if language == 'ru':
            honeypot_true_msg = f"❗️ Токен {token_address} <b>ЯВЛЯЕТСЯ</b> мошенническим!"
            honeypot_false_msg = f"✅ Токен {token_address} <b>НЕ</b> является мошенническим."
            risk_level_msg = f"Уровень риска: {data.get('summary', {}).get('risk', 'unknown')} ({data.get('summary', {}).get('riskLevel', 'N/A')})"
            http_error_msg = "❗️ Не удалось проверить токен из-за ошибки API. Пожалуйста, попробуйте позже."
            request_error_msg = "❗️ Не удалось проверить токен. Пожалуйста, попробуйте позже."
            invalid_address_msg = "❗️ Пожалуйста, укажите адрес токена после команды /scam_token."
        else:
            honeypot_true_msg = f"❗️ The token {token_address} <b>IS</b> a honeypot!"
            honeypot_false_msg = f"✅ The token {token_address} is <b>NOT</b> a honeypot."
            risk_level_msg = f"Risk level: {data.get('summary', {}).get('risk', 'unknown')} ({data.get('summary', {}).get('riskLevel', 'N/A')})"
            http_error_msg = "❗️ Failed to check the token due to an API error. Please try again later."
            request_error_msg = "❗️ Failed to check the token. Please try again later."
            invalid_address_msg = "❗️ Please provide a token address after the /scam_token command."

        # Обработка результата Honeypot проверки
        if data['honeypotResult']['isHoneypot']:
            await message.answer(honeypot_true_msg, parse_mode='HTML')
        else:
            await message.answer(honeypot_false_msg, parse_mode='HTML')

        # Дополнительная информация о рисках
        await message.answer(risk_level_msg, parse_mode='HTML')
    
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        await message.answer(http_error_msg, parse_mode='HTML')
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        await message.answer(request_error_msg, parse_mode='HTML')
    
    except IndexError:
        await message.answer(invalid_address_msg, parse_mode='HTML')



@dp.message(Command(commands=['scam_liquidity']))
async def scam_liquidity_handler(message: types.Message):
    try:
        # Получаем язык пользователя из базы данных
        user_language = get_user_language(message.from_user.id)

        # Сообщения для двух языков
        invalid_address_msg = "❗️ Please provide a token address after the /scam_liquidity command." if user_language == 'en' else "❗️ Пожалуйста, укажите адрес токена после команды /scam_liquidity."
        no_liquidity_msg = "❗️ No liquidity found for the token." if user_language == 'en' else "❗️ Ликвидность для токена не найдена."
        
        # Извлечение адреса токена из сообщения
        try:
            token_address = message.text.split()[1]
        except IndexError:
            await message.answer(invalid_address_msg, parse_mode='HTML')
            return

        # Логируем начало процесса проверки
        logging.info(f"Checking liquidity for token address: {token_address}")
        
        # Выполняем GET запрос к Honeypot API (в этом случае к endpoint для проверки ликвидности)
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',  # Нужно заменить на корректный URL для проверки ликвидности
            params={'address': token_address}
        )
        
        # Проверяем, если запрос выполнен успешно
        response.raise_for_status()
        
        # Логируем успешный запрос
        logging.info(f"Received liquidity response for token address: {token_address}")

        data = response.json()

        # Проверка наличия ликвидности
        if not data.get('pair'):
            await message.answer(no_liquidity_msg, parse_mode='HTML')
        else:
            # Проверка существования поля 'name' в объекте 'pair'
            liquidity = data['pair'].get('liquidity', 'N/A')

            # Формируем и отправляем сообщение с результатами ликвидности
            result_msg = (f"💧 The token {token_address} has liquidity and can be traded on DEX." 
                          if user_language == 'en' else 
                          f"💧 Токен {token_address} имеет ликвидность и может торговаться на DEX.")
            await message.answer(result_msg, parse_mode='HTML')

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        error_msg = "❗️ Failed to check the token due to an API error. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен из-за ошибки API. Попробуйте позже."
        await message.answer(error_msg)
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        error_msg = "❗️ Failed to check the token. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен. Пожалуйста, попробуйте позже."
        await message.answer(error_msg)




@dp.message(Command(commands=['scam_flags']))
async def scam_flags_handler(message: types.Message):
    try:
        # Получаем язык пользователя из базы данных
        user_language = get_user_language(message.from_user.id)

        # Сообщения для двух языков
        invalid_address_msg = "❗️ Please provide a token address after the /scam_flags command." if user_language == 'en' else "❗️ Пожалуйста, укажите адрес токена после команды /scam_flags."
        no_flags_msg = "✅ No flags found for this token." if user_language == 'en' else "✅ Флаги для этого токена не найдены."
        error_msg = "❗️ Failed to check the token. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен. Попробуйте позже."

        # Извлечение адреса токена из сообщения
        try:
            token_address = message.text.split()[1]
        except IndexError:
            await message.answer(invalid_address_msg, parse_mode='HTML')
            return

        # Логируем начало процесса проверки
        logging.info(f"Checking flags for token address: {token_address}")

        # Выполняем GET запрос к Honeypot API для получения флагов
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',  # Замените на правильный URL для флагов токена, если есть другой эндпоинт
            params={'address': token_address}
        )

        # Проверяем, если запрос выполнен успешно
        response.raise_for_status()

        # Логируем успешный запрос
        logging.info(f"Received flags response for token address: {token_address}")

        data = response.json()

        # Проверка наличия флагов
        flags = data.get('flags', [])
        if not flags:
            await message.answer(no_flags_msg, parse_mode='HTML')
        else:
            # Формируем и отправляем сообщение с флагами
            flag_messages = []
            for flag in flags:
                severity = flag.get('severity', 'N/A')
                description = flag.get('description', 'No description available')

                # Эмодзи в зависимости от степени тяжести флага
                if severity == 'critical':
                    emoji = "🔴"
                elif severity == 'high':
                    emoji = "🟠"
                elif severity == 'medium':
                    emoji = "🟡"
                else:
                    emoji = "🔵"  # Низкий уровень или информационные сообщения

                # Создание сообщения для каждого флага
                flag_msg = f"{emoji} <b>{severity.capitalize()}</b>: {description}"
                flag_messages.append(flag_msg)

            # Объединяем все флаги в одно сообщение
            flags_result = "\n".join(flag_messages)

            result_msg = (f"⚠️ <b>Token Flags:</b>\n{flags_result}" if user_language == 'en'
                          else f"⚠️ <b>Флаги токена:</b>\n{flags_result}")
            await message.answer(result_msg, parse_mode='HTML')

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        await message.answer(error_msg, parse_mode='HTML')
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        await message.answer(error_msg, parse_mode='HTML')



@dp.message(Command(commands=['scam_limits']))
async def scam_limits_handler(message: types.Message):
    try:
        # Получаем язык пользователя из базы данных
        user_language = get_user_language(message.from_user.id)

        # Сообщения для двух языков
        invalid_address_msg = "❗️ Please provide a token address after the /scam_limits command." if user_language == 'en' else "❗️ Пожалуйста, укажите адрес токена после команды /scam_limits."
        no_limits_msg = "✅ No buy or sell limits found for this token." if user_language == 'en' else "✅ Лимиты на покупку или продажу токенов не найдены."
        
        # Извлечение адреса токена из сообщения
        try:
            token_address = message.text.split()[1]
        except IndexError:
            await message.answer(invalid_address_msg, parse_mode='HTML')
            return

        # Логируем начало процесса проверки
        logging.info(f"Checking buy/sell limits for token address: {token_address}")
        
        # Выполняем GET запрос к Honeypot API
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',
            params={'address': token_address}
        )
        
        # Проверяем, если запрос выполнен успешно
        response.raise_for_status()
        
        # Логируем успешный запрос
        logging.info(f"Received buy/sell limits response for token address: {token_address}")

        data = response.json()

        # Проверка наличия лимитов на покупку и продажу
        max_buy = data.get('simulationResult', {}).get('maxBuy', {}).get('token', None)
        max_sell = data.get('simulationResult', {}).get('maxSell', {}).get('token', None)

        # Если лимиты на покупку и продажу не найдены
        if not max_buy and not max_sell:
            await message.answer(no_limits_msg, parse_mode='HTML')
        else:
            # Формируем и отправляем сообщение с результатами лимитов
            buy_msg = f"💰 <b>Max buy</b>: {max_buy} tokens" if max_buy else ""
            sell_msg = f"💰 <b>Max sell</b>: {max_sell} tokens" if max_sell else ""
            
            if user_language == 'en':
                result_msg = f"{buy_msg}\n{sell_msg}" if buy_msg or sell_msg else no_limits_msg
            else:
                result_msg = f"{buy_msg}\n{sell_msg}" if buy_msg or sell_msg else "✅ Лимиты на покупку или продажу токенов не найдены."

            await message.answer(result_msg, parse_mode='HTML')

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        error_msg = "❗️ Failed to check the token due to an API error. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен из-за ошибки API. Попробуйте позже."
        await message.answer(error_msg)
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        error_msg = "❗️ Failed to check the token. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен. Пожалуйста, попробуйте позже."
        await message.answer(error_msg)






@dp.message(Command(commands=['scam_fees']))
async def scam_gas_fees_handler(message: types.Message):
    try:
        # Получаем язык пользователя из базы данных
        user_language = get_user_language(message.from_user.id)

        # Сообщения для двух языков
        invalid_address_msg = "❗️ Please provide a token address after the /scam_fees command." if user_language == 'en' else "❗️ Пожалуйста, укажите адрес токена после команды /scam_fees."
        low_fees_msg = "💸 Low fees. Buy: {buy_gas} GWEI, Sell: {sell_gas} GWEI." if user_language == 'en' else "💸 Низкие комиссии. Покупка: {buy_gas} GWEI, Продажа: {sell_gas} GWEI."
        high_fees_msg = "⚠️ High fees! Buy: {buy_gas} GWEI, Sell: {sell_gas} GWEI." if user_language == 'en' else "⚠️ Высокие комиссии! Покупка: {buy_gas} GWEI, Продажа: {sell_gas} GWEI."
        
        # Извлечение адреса токена из сообщения
        try:
            token_address = message.text.split()[1]
        except IndexError:
            await message.answer(invalid_address_msg, parse_mode='HTML')
            return

        # Логируем начало процесса проверки
        logging.info(f"Checking gas fees for token address: {token_address}")
        
        # Выполняем GET запрос к Honeypot API
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',
            params={'address': token_address}
        )
        
        # Проверяем, если запрос выполнен успешно
        response.raise_for_status()
        
        # Логируем успешный запрос
        logging.info(f"Received gas fees response for token address: {token_address}")

        data = response.json()

        # Извлечение данных по газовым сборам
        buy_gas = data.get('simulationResult', {}).get('buyGas', None)
        sell_gas = data.get('simulationResult', {}).get('sellGas', None)

        # Проверка и вывод сообщения в зависимости от величины комиссий
        if buy_gas and sell_gas:
            buy_gas = int(buy_gas)
            sell_gas = int(sell_gas)

            # Определяем уровень комиссий
            if buy_gas < 100 and sell_gas < 100:
                result_msg = low_fees_msg.format(buy_gas=buy_gas, sell_gas=sell_gas)
            else:
                result_msg = high_fees_msg.format(buy_gas=buy_gas, sell_gas=sell_gas)

            await message.answer(result_msg, parse_mode='HTML')

        else:
            # Сообщение, если данные по комиссиям не были найдены
            no_fees_msg = "❗️ No gas fee data found for this token." if user_language == 'en' else "❗️ Данные о комиссиях не найдены для этого токена."
            await message.answer(no_fees_msg, parse_mode='HTML')

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        error_msg = "❗️ Failed to check the token due to an API error. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен из-за ошибки API. Попробуйте позже."
        await message.answer(error_msg)
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        error_msg = "❗️ Failed to check the token. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен. Пожалуйста, попробуйте позже."
        await message.answer(error_msg)





@dp.message(Command(commands=['scam_holder_analysis']))
async def scam_holder_analysis_handler(message: types.Message):
    try:
        # Получаем язык пользователя
        user_language = get_user_language(message.from_user.id)

        # Сообщения для двух языков
        invalid_address_msg = "❗️ Please provide a token address after the /scam_holder_analysis command." if user_language == 'en' else "❗️ Пожалуйста, укажите адрес токена после команды /scam_holder_analysis."

        # Извлечение адреса токена из сообщения
        try:
            token_address = message.text.split()[1]
        except IndexError:
            await message.answer(invalid_address_msg, parse_mode='HTML')
            return

        # Логируем начало процесса проверки
        logging.info(f"Checking holder analysis for token address: {token_address}")
        
        # Выполняем запрос к Honeypot API
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',
            params={'address': token_address}
        )
        
        # Проверка успешности запроса
        response.raise_for_status()

        # Получение данных из ответа
        data = response.json()

        # Проверяем, содержит ли ответ данные о holderAnalysis
        if 'holderAnalysis' in data:
            successful_holders = int(data['holderAnalysis']['successful'])
            failed_holders = int(data['holderAnalysis']['failed'])

            # Если все владельцы могут продать свои токены
            if failed_holders == 0:
                success_message = "✅ All holders successfully sold their tokens." if user_language == 'en' else "✅ Все владельцы успешно продали свои токены."
                await message.answer(success_message, parse_mode='HTML')
            else:
                failure_message = (f"⚠️ Some holders cannot sell their tokens! Number of holders with issues: {failed_holders}." 
                                   if user_language == 'en' else 
                                   f"⚠️ Некоторые владельцы не могут продать свои токены! Количество владельцев с проблемами: {failed_holders}.")
                await message.answer(failure_message, parse_mode='HTML')
        else:
            # Если информация о holderAnalysis отсутствует
            no_data_message = "❗️ No holder analysis data available for this token." if user_language == 'en' else "❗️ Данные о владельцах для этого токена отсутствуют."
            await message.answer(no_data_message, parse_mode='HTML')

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        error_message = "❗️ Failed to analyze the token due to an API error. Please try again later." if user_language == 'en' else "❗️ Не удалось выполнить анализ токена из-за ошибки API. Попробуйте позже."
        await message.answer(error_message)
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        error_message = "❗️ Failed to analyze the token. Please try again later." if user_language == 'en' else "❗️ Не удалось выполнить анализ токена. Пожалуйста, попробуйте позже."
        await message.answer(error_message)



@dp.message(Command(commands=['scam_contract']))
async def scam_contract_handler(message: types.Message):
    try:
        # Получаем язык пользователя из базы данных
        user_language = get_user_language(message.from_user.id)

        # Сообщения для двух языков
        invalid_address_msg = "❗️ Please provide a token address after the /scam_contract command." if user_language == 'en' else "❗️ Пожалуйста, укажите адрес токена после команды /scam_contract."
        no_contract_data_msg = "❗️ No contract data available for this token." if user_language == 'en' else "❗️ Нет данных о контракте для данного токена."
        contract_open_msg = "✅ The smart contract is open-source and contains no proxy calls." if user_language == 'en' else "✅ Смарт-контракт имеет открытый исходный код и не содержит прокси-вызовов."
        contract_closed_msg = "⚠️ Warning! The smart contract is closed and may contain hidden functions." if user_language == 'en' else "⚠️ Внимание! Смарт-контракт закрыт и может содержать скрытые функции."
        
        # Извлечение адреса токена из сообщения
        try:
            token_address = message.text.split()[1]
        except IndexError:
            await message.answer(invalid_address_msg, parse_mode='HTML')
            return

        # Логируем начало процесса проверки
        logging.info(f"Checking contract for token address: {token_address}")
        
        # Выполняем GET запрос к Honeypot API для анализа контракта
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',  # Убедитесь, что это правильный эндпоинт
            params={'address': token_address}
        )
        
        # Проверяем, если запрос выполнен успешно
        response.raise_for_status()

        # Логируем успешный запрос
        logging.info(f"Received contract data for token address: {token_address}")

        data = response.json()

        # Проверка наличия данных о контракте
        if 'contractCode' not in data:
            await message.answer(no_contract_data_msg, parse_mode='HTML')
            return
        
        contract_data = data['contractCode']

        # Проверка, открыт ли исходный код и есть ли прокси-вызовы
        if contract_data.get('openSource', False) and not contract_data.get('hasProxyCalls', False):
            await message.answer(contract_open_msg, parse_mode='HTML')
        else:
            await message.answer(contract_closed_msg, parse_mode='HTML')

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        error_msg = "❗️ Failed to check the token due to an API error. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен из-за ошибки API. Попробуйте позже."
        await message.answer(error_msg)
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        error_msg = "❗️ Failed to check the token. Please try again later." if user_language == 'en' else "❗️ Не удалось проверить токен. Пожалуйста, попробуйте позже."
        await message.answer(error_msg)







@dp.message(Command(commands=['scam_simulate_trade']))
async def scam_simulate_trade_handler(message: types.Message):
    try:
        # Получаем язык пользователя из базы данных
        user_language = get_user_language(message.from_user.id)

        # Сообщения для двух языков
        invalid_address_msg = "❗️ Please provide a token address after the /scam_simulate_trade command." if user_language == 'en' else "❗️ Пожалуйста, укажите адрес токена после команды /scam_simulate_trade."
        simulation_failed_msg = "❌ Simulation failed. Issues with liquidity or inability to sell the token." if user_language == 'en' else "❌ Симуляция не удалась. Проблемы с ликвидностью или невозможность продать токен."
        simulation_successful_msg = "✅ Simulation successful. The token can be sold on the market with minimal issues." if user_language == 'en' else "✅ Симуляция успешна. Токен можно продать на рынке с минимальными проблемами."
        
        # Извлечение адреса токена из сообщения
        try:
            token_address = message.text.split()[1]
        except IndexError:
            await message.answer(invalid_address_msg, parse_mode='HTML')
            return

        # Логируем начало процесса симуляции
        logging.info(f"Simulating trade for token address: {token_address}")
        
        # Выполняем GET запрос к Honeypot API для симуляции торговли
        response = requests.get(
            'https://api.honeypot.is/v2/IsHoneypot',  # Здесь корректный URL для симуляции торговли
            params={'address': token_address, 'simulateLiquidity': True}
        )
        
        # Проверяем успешность запроса
        response.raise_for_status()

        # Логируем успешный запрос
        logging.info(f"Received simulation response for token address: {token_address}")

        data = response.json()

        # Проверка успешности симуляции
        if data.get('simulationSuccess', False):
            await message.answer(simulation_successful_msg, parse_mode='HTML')
        else:
            await message.answer(simulation_failed_msg, parse_mode='HTML')

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        error_msg = "❗️ Failed to simulate the trade due to an API error. Please try again later." if user_language == 'en' else "❗️ Не удалось выполнить симуляцию из-за ошибки API. Попробуйте позже."
        await message.answer(error_msg)
    
    except requests.exceptions.RequestException as err:
        logging.error(f"Error occurred: {err}")
        error_msg = "❗️ Failed to simulate the trade. Please try again later." if user_language == 'en' else "❗️ Не удалось выполнить симуляцию. Пожалуйста, попробуйте позже."
        await message.answer(error_msg)
    
    except IndexError:
        await message.answer(invalid_address_msg, parse_mode='HTML')


