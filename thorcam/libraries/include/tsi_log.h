/*
* Copyright 2019 by Thorlabs, Inc.  All rights reserved.  Unauthorized use (including,
* without limitation, distribution and copying) is strictly prohibited.  All use requires, and is
* subject to, explicit written authorization and nondisclosure agreements with Thorlabs, Inc.
*/

/*! \mainpage Thorlabs Scientific Logger
*
* \section Introduction
*
* The target audience for this document is a software professional who wants to incorporate
* their component into the TSI logging framework.
*
*/

#pragma once

/*! \file tsi_log.h
*   \brief This file includes the declaration prototypes of all the API functions 
*          contained in the logger module.
*/

/*! This function creates a handle to a logger based on the specified parameters.
*  
*   \param[in] moduleID A character string identifying the name of the module containing the statements to log
*   \param[in] groupID A character string identifying an alternate name to use when creating a logger.
*                      This name should be different than the moduleID and is used to subclass a logger from
*                      the primary identifier which is the groupID.
*   \returns A handle to a logger.
*/
typedef void* (*TSI_GET_LOG) (const char*, const char*);

/*! This function will log the specified statement according to the specified parameters.
*
*   \param[in] logger A handle to the desired logger.
*   \param[in] priority A character string indicating the log priority.
*                       Valid values are:
*                       - "Fatal"
*                       - "Critical"
*                       - "Error"
*                       - "Warning"
*                       - "Notice"
*                       - "Information"
*                       - "Debug"
*                       - "Trace"
*   \param[in] file_name The file name containing the statement to log.
*   \param[in] file_line The line number in the file containing the statement to log.
*   \param[in] function_name The name of the function containing the statement to log.
*   \param[in] msg The statement to log.
*   \returns 0 to indicate success and 1 to indicate failure.
*/
typedef int (*TSI_LOG) (void*, const char*, const char*, int, const char*, const char*);

/*! This function destroys the logger with the specified parameters.
*  
*   \param[in] moduleID A character string identifying the name of the module containing the statements to log
*   \param[in] groupID A character string identifying an alternate name to use when creating a logger.
*                      This name should be different than the moduleID and is used to subclass a logger from
*                      the primary identifier which is the groupID.
*/
typedef void (*TSI_FREE_LOG) (const char*, const char*);
